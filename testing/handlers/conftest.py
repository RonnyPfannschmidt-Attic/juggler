from mock import Mock
from juggler import utils, service


def pytest_generate_tests(metafunc):
    if 'db' in metafunc.funcargnames:
        l = ['direct', 'mocked']
        metafunc.parametrize('db', l, ids=l, indirect=True)


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
            super(FakedDatabase, self).refresh(doc)

    def get(self, *k, **kw):
        return self.db.get(*k, **kw)

    def watch_for(self, type, **kw):
        if self.real_db:
            return utils.watch_for(self.db, type, **kw)
        raise RuntimeError('no real db and not overridden')

    def all_current_docs_for(self, item):
        #XXX: real implementation
        return []

    def save_doc(self, doc):
        #XXX: hack
        if 'watch_for' not in vars(self) and self.real_db is None:
            self.watch_for = faked_watch_for(doc)
        else:
            self.db.save_doc(doc)

    def bulk_save(self, *k, **kw):
        self.db.bulk_save(*k, **kw)


def pytest_funcarg__db(request):
    if request.param == 'direct':
        db = request.getfuncargvalue('couchdb')
    else:
        db = None
    return FakedDatabase(db)
