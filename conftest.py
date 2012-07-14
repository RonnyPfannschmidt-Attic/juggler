import py
root = py.path.local(__file__).dirpath()
composeapp = root.join('composeapp')


def pytest_runtest_setup(item):
    from juggler.handlers import utils
    extra = item.keywords.get('changes_extra')
    if extra:
        utils._CHANGES_EXTRA.update(extra.kwargs)

def pytest_runtest_teardown():
    from juggler.handlers import utils
    utils._CHANGES_EXTRA = {}

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
