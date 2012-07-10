class Juggler(object):
    def __init__(self, db):
        #XXX: assert gevent backend
        self.db = db

    def __repr__(self):
        return '<Juggler %r>' % self.db.dbname

    def store(self, obj):
        self.db.save_doc(obj)
