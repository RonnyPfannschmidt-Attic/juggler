from couchdbkit.exceptions import ResourceConflict
from ..model import Task
from .utils import watches_for

from logbook import Logger
log = Logger('slave')


@watches_for(Task, 'pending')
def claim_pending_task(db, task, owner):
    task.status = 'claiming'
    task.owner = owner.name
    try:
        db.save_doc(task)
        log.info(
            'claiming task {task._id} for {owner.name}',
            task=task, owner=owner,
        )
        return task
    except ResourceConflict:
        # its important to ignore conflicts here
        # it just means something already claimed
        # no need to generate more conflict
        log.info(
            'claiming task {task._id} for {owner.name} failed',
            task=task, owner=owner,
        )


@watches_for(Task, 'claimed', _id=lambda kw: kw['id'])
def wait_for_one_claiming_task(db, task, id, owner):
    log.info(
        "worker {owner.name} waited for {task._id} of {task.owner}",
        owner=owner, task=task,
    )
    if task.owner == owner.name:
        return task


@watches_for(Task, 'claimed', owner=lambda kw: kw['owner'].name)
def run_one_claimed_task(db, task, owner):
    log.info('dispatching task {task._id}', task=task)
    owner.run(task)
