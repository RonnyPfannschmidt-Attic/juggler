from logbook import Logger
from juggler.handlers import inbox, manage, utils

log = Logger('Master')  # , level='info')


callbacks_workers = [
    inbox.order_validate,
    inbox.valid_order_prepare,
    inbox.ready_order_generate_tasks,
    manage.new_task_generate_steps,
    manage.approve_claimed_task,
]


def make_callbacks(items):
    result = {}
    for func in items:
        result[func.type._doc_type, func.status] = func
    return result


def run_master(juggler, name, callbacks):
    #XXX: heartbeat
    viewresult = juggler.db.view(
        'juggler/stm',
        keys=callbacks.keys(),
        include_docs=True,
        reduce=False,
        update_seq=True,
    )
    log.info('walking stm view result')
    for row in viewresult.all():
        dispatch_doc(juggler, row['doc'], callbacks)

    log.info('walking changes since {seq}', seq=viewresult.update_seq)
    new_changes = utils.listen_new_changes(juggler.db,
                                           since=viewresult.update_seq)
    for change in new_changes:
        dispatch_doc(juggler, change['doc'], callbacks)


def dispatch_doc(db, doc, callbacks):
    lookup = str(doc['type']), str(doc['status'])
    log.debug('event {} for {}', lookup, doc['_id'])
    call = callbacks.get(lookup)
    if call is not None:
        obj = call.type.wrap(doc)
        log.info('call {call.__name__} for {obj.type} {obj._id}',
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
