from juggler.handlers import slave


def run_once(service):
    claiming = slave.claim_pending_task(service, owner=service)
    task = slave.wait_for_one_claiming_task(service, id=claiming._id)
    if task is not None:
        slave.run_one_claimed_task(service, task, owner=service)
