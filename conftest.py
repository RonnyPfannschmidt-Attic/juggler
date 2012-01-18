

def pytest_funcarg__couchdb(request):
    from couchdbkit import Server
    return request.cached_setup(Server, scope='session')

def pytest_funcarg__juggler(request):
    server = request.getfuncargvalue('couchdb')
    item = request._pyfuncitem
    names = [x.replace('/','__').replace('.py','') for x in item.listnames()[1:]]
    dbname = '__'.join(names)
    db = server.get_or_create_db(dbname)
    db.flush()
    from juggler.model import setup_design
    setup_design(db)

    from juggler.app import Juggler
    return Juggler(db)
