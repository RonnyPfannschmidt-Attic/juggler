

def pytest_funcarg__juggler(request):
    db = request.getfuncargvalue('couchdb')

    from juggler.model import setup_design
    setup_design(db)

    from juggler.app import Juggler
    app = Juggler(db)
    request.addfinalizer(app._background_job.kill)
    return app
