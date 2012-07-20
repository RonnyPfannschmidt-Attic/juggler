from logbook import Logger
from ..model import Task, Project
from .utils import watches_for, steps_from_template

log = Logger('shedule', level='info')


@watches_for(Task, 'new')
def new_task_generate_steps(db, task):
    log.debug('get project {}', task.project)
    project = db.get(task.project, schema=Project)
    log.debug('got {}', project)
    bulk = [task]
    if project.computed_steps:
        raise NotImplementedError
        task.status = 'preparing'
    else:
        bulk += steps_from_template(project, task)
        task.status = 'pending'
    log.debug('save_bulk, {}', bulk)
    db.bulk_save(bulk)
    log.info('generated steps for {task._id}', task=task)


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
            log.info('claiming {task._id} for {task.owner} failed', task=task)

            break
    else:
        # no solution yet, accept the claim
        task.status = 'claimed'
        db.save_doc(task)
        log.info('claimed {task._id} for {task.owner}', task=task)
