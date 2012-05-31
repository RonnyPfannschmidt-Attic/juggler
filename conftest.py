import py
root = py.path.local(__file__).dirpath()
kansoapp = root/'kansoapp'

def pytest_funcarg__ghost_base(request):
    db = request.getfuncargvalue('couchdb')
    return db.res.uri + '/_design/juggler/_rewrite'

def pytest_couchdbkit_push_app(dbname):
    py.std.subprocess.check_call(['kanso', 'install'], cwd=str(kansoapp))
    py.std.subprocess.check_call(['kanso', 'push', dbname], cwd=str(kansoapp))

def pytest_funcarg__juggler(request):
    db = request.getfuncargvalue('couchdb')

    from juggler.service import Juggler
    app = Juggler(db)
    request.addfinalizer(app._background_job.kill)
    return app
