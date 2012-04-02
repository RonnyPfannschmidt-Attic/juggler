import itertools
from . import model

import gevent

from couchdbkit.changes import ChangesStream

def generate_specs(axis):
    if not axis:
        yield None
        return

    names, lists = zip(*axis.items())
    for values in itertools.product(*lists):
        yield dict(zip(names, values))


class Juggler(object):
    def __init__(self, db):
        #XXX: assert gevent backend
        self.db = db
        self._background_job = gevent.spawn(self.handle_db_change)
        gevent.sleep(0)

    def __repr__(self):
        return '<Juggler %r>'%self.db.dbname

    def store(self, obj):
        self.db.save_doc(obj)

    def shedule_task(self, order):
        assert '_id' in order:
        bulk = [order]
        for spec in generate_specs(order['axis']):
            job = {
                'type': 'juggler.task',
                'arbiter': 'glas_process', # magic constant
                'receipe': order['receipe'],
                'order': order['_id'],
                spec=spec,
            )
            bulk.append(job)

        order['status'] = 'building'
        self.db.bulk_save(bulk, all_or_nothing=True)

    def handle_db_change(self):

        stream = ChangesStream(self.db, feed='continuous')
        for data in stream:
            obj = self.db.get(data['id'], wrapper=model.wrap)
            if isinstance(obj, dict) and obj.get('_id').startswith('_design'):
                return
            print 'changed', obj


