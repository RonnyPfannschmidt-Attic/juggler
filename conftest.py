import py
root = py.path.local(__file__).dirpath()
kansoapp = root/'kansoapp'

def pytest_couchdbkit_push_app(dbname):
    py.std.subprocess.check_call(['kanso', 'install'], cwd=str(kansoapp))
    py.std.subprocess.check_call(['kanso', 'push', dbname], cwd=str(kansoapp))

def pytest_funcarg__juggler(request):
    db = request.getfuncargvalue('couchdb')

    from juggler.app import Juggler
    app = Juggler(db)
    request.addfinalizer(app._background_job.kill)
    return app
