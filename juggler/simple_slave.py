import py
from juggler.handlers import work


def simple(service, args=None):
    #XXX hack
    #XXX: better basedir
    if service.path is None:
        basedir = py.path.local(service.name).ensure(dir=1)
        service.path = basedir

    while True:
        run_once(service)


def run_once(service):
    claiming = work.claim_pending_task(service, owner=service)
    if claiming is None:
        return
    task = work.wait_for_one_claiming_task(service,
                                           id=claiming._id,
                                           owner=service)
    if task is not None:
        work.run_one_claimed_task(service, task,
                                  owner=service.name,
                                  run=service.run_task)
