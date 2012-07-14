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
    #XXX: better basedir
    import py
    basedir = py.path.local(service.name).ensure(dir=1)
    from juggler.process.arbiter import Arbiter
    arbiter = Arbiter(service.db, basedir)
    if task is not None:
        #XXX rename owner arg
        slave.run_one_claimed_task(service, task, owner=arbiter)
