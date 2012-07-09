import itertools
from . import model

import gevent

from couchdbkit.changes import ChangesStream



class Juggler(object):
    def __init__(self, db):
        #XXX: assert gevent backend
        self.db = db
        self._background_job = gevent.spawn(self.handle_db_change)
        gevent.sleep(0)

    def __repr__(self):
        return '<Juggler %r>' % self.db.dbname

    def store(self, obj):
        self.db.save_doc(obj)



