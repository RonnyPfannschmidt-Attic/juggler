def pytest_funcarg__procdir(request):
    tmpdir = request.getfuncargvalue('tmpdir')
    db = request.getfuncargvalue('couchdb')
    testname = nodeid = request._pyfuncitem.nodeid
    nodeid = nodeid.replace('.py', '').replace('::', '.')
    from juggler.process.procdir import ProcDir
    from juggler.model import Task

    task = Task(_id=nodeid, owner=testname)
    db.save_doc(task)
    procdir = ProcDir(db, tmpdir.join('proc'), task)
    if 'no_create' not in request._pyfuncitem.keywords:
        procdir.path.ensure(dir=1)
    return procdir
