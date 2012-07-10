from mock import Mock
from juggler import workers
from juggler import model


def faked_watch_for(result, info=None):
    def faked_watch_for(db, type, **kw):
        assert isinstance(result, type)
        for k, v in kw.items():
            assert getattr(result, k) == v

        return result, info
    return faked_watch_for


def test_inbox_simple_validate():
    #XXX: test a invalid case
    db = Mock()
    order = model.Order(status='received')
    watch_for = faked_watch_for(order)
    workers.inbox_validate(db, watch_for)
    assert order.status == 'valid'
    db.save_doc.assert_called_with(order)


def test_valid_order_simple_ready():
    db = Mock()
    order = model.Order(status='valid')
    watch_for = faked_watch_for(order)
    workers.valid_order_prepare(db, watch_for)
    assert order.status == 'ready'
    db.save_doc.assert_called_with(order)


def test_ready_order_generate_tasks():
    db = Mock()
    order = model.Order(status='ready', axis=None)
    watch_for = faked_watch_for(order)
    workers.ready_order_generate_tasks(db, watch_for)
    assert order.status == 'building'
    saved_order, saved_task = db.bulk_save.call_args[0][0]
    assert saved_order is order
    assert saved_task.spec == {}
