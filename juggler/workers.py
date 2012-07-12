import copy
from itertools import product
from functools import wraps
from couchdbkit.exceptions import ResourceConflict
from .model import Order, Task, Project


def steps_from_template(project, task):
    return copy.deepcopy(project.steps) or []


def generate_specs(axis):
    if not axis:
        yield {}
        return

    names, lists = zip(*sorted(axis.items()))
    for values in product(*lists):
        yield dict(zip(names, values))


def watches_for(type, status, **wkw):
    def decorator(func):
        @wraps(func)
        def watching_version(db, *k, **kw):
            if k:
                item, = k
            else:
                watch_kw = {}
                for key, val in wkw.items():
                    watch_kw[key] = val(kw)

                item, _ = db.watch_for(type, status=status, **watch_kw)
            return func(db, item, *k, **kw)
        watching_version.type = type
        watching_version.status = status
        watching_version.func = func
        return watching_version
    return decorator


@watches_for(Order, 'received')
def inbox_validate(db, order):
    #XXX: validate
    order.status = 'valid'
    db.save_doc(order)


@watches_for(Order, 'valid')
def valid_order_prepare(db, order):
    #XXX: fill in axis from project/task
    order.status = 'ready'
    db.save_doc(order)


@watches_for(Order, 'ready')
def ready_order_generate_tasks(db, order):
    bulk = [order]
    oid = order._id
    for idx, spec in enumerate(generate_specs(order.axis)):
        #XXX: steps
        job = Task(
            _id='%s.task%s' % (oid, idx),
            # currently unused magic constant
            arbiter='glas_process',
            order=oid,
            spec=spec,
            index=idx,
        )
        bulk.append(job)

    order.status = 'building'
    db.bulk_save(bulk)


@watches_for(Task, 'new')
def new_task_generate_steps(db, task):
    project = db.get(task.project, schema=Project)
    bulk = [task]
    if project.computed_steps:
        raise NotImplementedError
        task.status = 'preparing'
    else:
        bulk += steps_from_template(project, task)
        task.status = 'pending'
    db.bulk_save(bulk)


@watches_for(Task, 'pending')
def claim_pending_task(db, task, owner):
    task.status = 'claiming'
    task.owner = owner
    try:
        db.save_doc(task)
        return task
    except ResourceConflict:
        # its important to ignore conflicts here
        # it just means something already claimed
        # no need to generate more conflict
        #XXX log about failed claim
        pass


@watches_for(Task, 'claiming')
def approve_claimed_task(db, task):
    # this asumes only one claim manager is running ever
    # we operate on a first come first serve basis
    all_docs = db.all_current_docs_for(task)

    for doc in all_docs:
        if doc._rev != task._rev and doc.status != 'claiming':
            # conflict already solved by one
            # of the contenders proceeding
            # delete that exact revision
            db.delete_doc(task)
            break
    else:
        # no solution yet, accept the claim
        task.status = 'claimed'
        db.save_doc(task)


@watches_for(Task, 'claimed', _id=lambda kw: kw['id'])
def wait_for_one_claiming_task(db, task, id, owner):
    if task.owner == owner:
        return task


@watches_for(Task, 'claimed', owner=lambda kw: kw['owner'].name)
def run_one_claimed_task(db, task, owner):
    owner.run(task)
