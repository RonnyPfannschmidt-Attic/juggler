from logbook import Logger
from juggler.handlers import inbox, shedule, utils

log = Logger('Master')


callbacks_workers = [
    inbox.order_validate,
    inbox.valid_order_prepare,
    inbox.ready_order_generate_tasks,
    shedule.new_task_generate_steps,
    shedule.approve_claimed_task,
]


def make_callbacks(items):
    result = {}
    for func in items:
        result[func.type._doc_type, func.status] = func
    return result


def run_master(db, name, callbacks):
    #XXX: heartbeat
    new_changes = utils.listen_new_changes(db.db)
    for change in new_changes:
        doc = change['doc']
        lookup = str(doc['type']), str(doc['status'])
        print lookup, change['id']
        call = callbacks.get(lookup)
        if call is not None:
            obj = call.type.wrap(doc)
            log.debug('call {call.__name__} for {obj.type} {obj._id}',
                      call=call, obj=obj)
            call.func(db, obj)  # protect against green exit


def simple_master(service, args=None):
    #XXX: heartbeat
    #XXX: filter
    #XXX: since
    callbacks = make_callbacks(callbacks_workers)
    import pprint
    pprint.pprint(callbacks)
    run_master(service, service.name, callbacks)
