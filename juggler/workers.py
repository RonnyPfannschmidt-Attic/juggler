from itertools import product
from couchdbkit.exceptions import ResourceConflict
from .model import Order, Task, Project


def all_current_docs_for(id, schema):
    pass


def steps_from_template(task, project):

    return []


def generate_specs(axis):
    if not axis:
        yield {}
        return

    names, lists = zip(*sorted(axis.items()))
    for values in product(*lists):
        yield dict(zip(names, values))


def inbox_validate(db):
    order, _ = db.watch_for(Order, status='received')
    #XXX: validate
    order.status = 'valid'
    db.save_doc(order)


def valid_order_prepare(db):
    order, _ = db.watch_for(Order, status='valid')
    #XXX: fill in axis from project/task
    order.status = 'ready'
    db.save_doc(order)


def ready_order_generate_tasks(db):
    order, _ = db.watch_for(Order, status='ready')
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


def new_task_generate_steps(db):
    task, _ = db.watch_for(Task, status='new')
    project = db.get(task.project, schema=Project)
    bulk = [task]
    if project.computed_steps:
        raise NotImplementedError
        task.status = 'preparing'
    else:
        bulk += steps_from_template(project, task)
        task.status = 'pending'
    db.bulk_save(bulk)


def claim_pending_task(db, owner):
    task, _ = db.watch_for(Task, status='pending')
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


def approve_claimed_task(db):
    # this asumes only one claim manager is running ever
    # we operate on a first come first serve basis
    task, info = db.watch_for(Task, status='claiming')
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


def run_one_claimed_task(db, owner):
    task, _ = db.watch_for(Task, status='claimed', owner=owner.name)
    owner.run(task)
