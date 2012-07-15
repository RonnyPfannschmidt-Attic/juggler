from ..model import Order, Task
from .utils import watches_for, generate_specs

from logbook import Logger
log = Logger('inbox')


@watches_for(Order, 'received')
def order_validate(db, order):
    #XXX: validate
    order.status = 'valid'
    db.save_doc(order)
    log.info('order {order._id} valid')


@watches_for(Order, 'valid')
def valid_order_prepare(db, order):
    #XXX: fill in axis from project/task
    order.status = 'ready'
    db.save_doc(order)
    log.info('order {order._id} ready')


@watches_for(Order, 'ready')
def ready_order_generate_tasks(db, order):
    bulk = [order]
    oid = order._id
    for idx, spec in enumerate(generate_specs(order.axis)):
        job = Task(
            _id='%s.task%s' % (oid, idx),
            # currently unused magic constant
            arbiter='glas_process',
            order=oid,
            project=order.project,
            spec=spec,
            index=idx,
        )
        bulk.append(job)

    order.status = 'building'
    db.bulk_save(bulk)
    log.info('order {order._id} building')
