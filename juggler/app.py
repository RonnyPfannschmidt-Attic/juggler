import json
import uuid
import itertools
from . import model
from couchdbkit.consumer import Consumer


def generate_specs(axis):
    if not axis:
        yield None
        return

    names, lists = zip(*axis.items())
    for values in itertools.product(*lists):
        yield dict(zip(names, values))


class Juggler(object):
    def __init__(self, db):
        self.db = db
        self._consumer = Consumer(db, backend='gevent')
        self._consumer.wait_async(self._handle_db_change)
    def __repr__(self):
        return '<Juggler %r>'%self.db.dbname

    def store(self, obj):
        self.db.save_doc(obj)

    def shedule_jobs(self, build):

        bulk = [build]
        for spec in generate_specs(build.axis):
            job = model.Job(
                project=build.project,
                build=build._id,
                spec=spec,
            )
            bulk.append(job)
            

        build.status = 'building'
        self.db.bulk_save(bulk, all_or_nothing=True)



    def _handle_db_change(self, line):
        data = json.loads(line)
        obj = self.db.get(data['id'], wrapper=model.wrap)
        if isinstance(obj, dict) and obj.get('_id').startswith('_design'):
            return
        
        print 'changed', obj

        

