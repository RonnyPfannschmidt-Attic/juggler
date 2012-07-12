import py
root = py.path.local(__file__).dirpath()
composeapp = root.join('composeapp')


def pytest_funcarg__ghost_base(request):
    db = request.getfuncargvalue('couchdb')
    return db.res.uri + '/_design/juggler/_rewrite'


def pytest_couchdbkit_push_app(dbname):
    py.std.subprocess.check_call([
        'couchdb-compose', 'push', dbname,
                           '--path', str(composeapp)
    ])


def pytest_funcarg__juggler(request):
    db = request.getfuncargvalue('couchdb')

    from juggler.service import Juggler
    app = Juggler(db, 'juggler')
    return app
