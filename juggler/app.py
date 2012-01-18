import uuid
from . import model

class Juggler(object):
    def __init__(self, db):
        self.db = db
    def __repr__(self):
        return '<Juggler %r>'%self.db.name

    def store(self, obj):
        self.db.save_doc(obj)

    def shedule_jobs(self, build):

        if not build.axis:
            job = model.Job(
                project=build.project,
                build=build._id,
                spec=None,
            )
            self.store(job)




    

