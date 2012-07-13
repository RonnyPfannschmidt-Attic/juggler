from juggler.handlers import slave


def claim(service, args):
    configure_claim(service, args)
    service.run()


def configure_claim(service, args):
    raise NotImplementedError


def configure_work(service, args):
    raise NotImplementedError
    pass


def work(service, args):
    raise NotImplementedError
    pass


def simple(service, args):
    while True:
        run_once(service)


def run_once(service):
    claiming = service.smart_watch(
        slave.claim_pending_task,
        owner=service)
    task = service.smart_watch(
        slave.wait_for_one_claiming_task,
        id=claiming._id, owner=service)
    if task is not None:
        slave.run_one_claimed_task(service, task, owner=service)
