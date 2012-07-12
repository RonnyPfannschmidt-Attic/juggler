import gevent
from .utils import watch_for


class Juggler(object):
    def __init__(self, db, name):
        #XXX: assert gevent backend
        self.name = name
        self.db = db

    def __repr__(self):
        return '<Juggler %r>' % self.db.dbname

    def watch_for(self, type, **kw):
        return watch_for(self.db, type,
                         timeout=5,
                         **kw)

    def save_doc(self, doc):
        self.db.save_doc(doc)

    def sleep(self):
        gevent.sleep(.5)
        return gevent

    def refresh(self, doc):
        schema = type(doc)
        new_doc = self.real_db.get(doc._id, schema=schema)
        doc._doc = new_doc._doc
