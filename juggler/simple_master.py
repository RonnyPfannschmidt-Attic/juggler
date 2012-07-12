from couchdb.changes import ChangeStream
from juggler import workers


callbacks_workers = [
    'inbox_validate',
    'valid_order_prepare',
    'ready_order_generate_tasks',
    'new_task_generate_steps',
    'approve_claimed_task',
]

def make_callbacks(items):
    result = {}
    for name in items:
        func = getattr(workers, name)
        result[f.type._doc_type, f.status] = f
    return result




                            

def run_master(juggler
    callbac


def run_master(db, name, new_changes, callbacks=None):
    callbacks = callbacks or make_callbacks()
    #XXX: heartbeat

    for change in new_changes:
        doc = change['doc']
        lookup = doc['type', 'doc'



    def start(self):


