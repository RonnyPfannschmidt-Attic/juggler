"""
warden encapsulates watching over multiple workers
"""

from . import model

class Warden(object):
    def __init__(self, db, doc):
        self.db = db
        self.doc = doc
        self.workers = {}


    def get_worker(self, id):
        if id in self.workers:
            return self.workers[id]
        else:
            doc = db.get(id, woker)
        worker = Worker(self, doc)





class Worker(object):
    def __init__(self, warden, doc):
        self.warden = warden
        self.doc = doc
