
from juggler import workers






def run_once(service):
    claiming = workers.claim_pending_task(db, owner=service)
    task = workers.wait_for_one_claiming_task(db, id=claiming._id)
    if task is not None:
        workers.run_one_claimed_task(task, owner=service)
