from mock import Mock
from juggler import service
from juggler.handlers import utils


def faked_watch_for(result, info=None):
    def faked_watch_for(type, **kw):
        assert isinstance(result, type)
        for k, v in kw.items():
            assert getattr(result, k) == v

        return result, info
    return faked_watch_for


class FakedDatabase(service.Juggler):
    def __init__(self, real_db=None):
        self.real_db = real_db
        if real_db is not None:
            self.db = Mock(wraps=real_db)
        else:
            self.db = Mock()
        self._ = self.db

    def refresh(self, doc):
        if self.real_db:
            schema = type(doc)
            new_doc = self.real_db.get(doc._id, schema=schema)
            doc._doc = new_doc._doc

    def watch_for(self, type, **kw):
        if self.real_db:
            return utils.watch_for(self.real_db, type, **kw)
        raise RuntimeError('no real db and not overridden')

    def save_doc(self, doc):
        #XXX: hack
        if 'watch_for' not in vars(self) and self.real_db is None:
            self.watch_for = faked_watch_for(doc)
        else:
            self.db.save_doc(doc)


def pytest_funcarg__db(request):
    db = request.getfuncargvalue('couchdb')
    return FakedDatabase(db)
