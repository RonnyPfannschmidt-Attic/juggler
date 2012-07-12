import gevent


class Juggler(object):
    def __init__(self, db, name):
        #XXX: assert gevent backend
        self.name = name
        self.db = db

    def __repr__(self):
        return '<Juggler %r>' % self.db.dbname

    def sleep(self):
        gevent.sleep(.5)
        return gevent
