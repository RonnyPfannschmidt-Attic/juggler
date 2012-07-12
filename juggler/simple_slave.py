from juggler import workers


def run_once(service):
    claiming = workers.claim_pending_task(service, owner=service)
    task = workers.wait_for_one_claiming_task(service, id=claiming._id)
    if task is not None:
        workers.run_one_claimed_task(service, task, owner=service)
