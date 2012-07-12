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
        result[func.type._doc_type, func.status] = func
    return result


def run_master(db, name, new_changes, callbacks=None):
    callbacks = callbacks or make_callbacks()
    #XXX: heartbeat

    for change in new_changes:
        doc = change['doc']
        lookup = doc['type', 'doc']
        call = callbacks.get(lookup)
        if call is not None:
            call(call.type.wrap(doc))
