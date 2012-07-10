from .model import Order, Task, Step


def generate_specs(axis):
    if not axis:
        yield {}
        return

    names, lists = zip(*axis.items())
    for values in itertools.product(*lists):
        yield dict(zip(names, values))


def inbox_validate(db, watch_for):
    order, _ = watch_for(db, Order, status='received')
    #XXX: validate
    order.status = 'valid'
    db.save_doc(order)


def valid_order_prepare(db, watch_for):
    order, _ = watch_for(db, Order, status='valid')
    #XXX: fill in axis from project/task
    order.status = 'ready'
    db.save_doc(order)


def ready_order_generate_tasks(db, watch_for):
    order, _ = watch_for(db, Order, status='ready')
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
    task, _ = watch_for(db, Task, status='new')
    project = project_of_task(db, task)
    bulk = [task]
    if project.computed_steps:

        bulk.append(compute_task)
        task.status = 'preparing'
    else:
        bulk += steps_from_template(project, task)
        task.status = 'pending'
    db.bulk_save(bulk)


def claim_pending_task(db, owner):
    task, _ = watch_for(db, Task, status='pending')
    task.status = 'claiming'
    task.owner = owner
    db.save_doc(task)



def approve_claimed_task(db):
    # this asumes only one claim manager is running ever
    task, info = watch_for(db, Task, status='claiming')
    all_docs = all_current_docs_for(task._id)
    for doc in all_docs:
        if doc._rev != task._rev and doc.status != 'claiming':
            # conflict already solved by one
            # of the contenders proceeding
            # delete that exact revision
            db.delete_doc(task)
            break
    else:
        task.status = 'claimed'
        db.save_doc(task)

def run_one_claimed_task(db, owner):
    task = watch_for(db, Task, status='claimed', owner=owner.name)
    arbiter = get_arbiter(ownert, task)
    arbiter.run()
