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
        return '<Juggler %r>' % self.db.dbname

    def store(self, obj):
        self.db.save_doc(obj)

    def shedule_task(self, order):
        assert order._id is not None
        bulk = [order]
        oid = order._id
        for idx, spec in enumerate(generate_specs(order['axis'])):
            
            job = model.Task(
                _id='%s.task%s' % (oid, idx),
                arbiter='glas_process',  # magic constant
                order=oid,
                spec=spec,
                index=idx,
            )
            bulk.append(job)

        order.status = 'building'
        self.db.bulk_save(bulk, all_or_nothing=True)

    def handle_db_change(self):

        stream = ChangesStream(self.db, feed='continuous')
        for data in stream:
            obj = self.db.get(data['id'], wrapper=model.wrap)
            if isinstance(obj, dict) and obj.get('_id').startswith('_design'):
                return
            print 'changed', obj


