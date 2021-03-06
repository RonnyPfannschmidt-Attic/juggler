import pytest
from juggler import model
from juggler.model import states as s
from juggler.handlers import inbox

from testing import with_quick_change_timeout


@with_quick_change_timeout
def test_inbox_simple_validate(db):
    #XXX: test a invalid case
    order = model.Order(_id='order', status=s.received)
    db.save_doc(order)
    inbox.order_validate(db)
    db.refresh(order)
    assert order.status == s.valid


@with_quick_change_timeout
def test_valid_order_simple_ready(db):
    order = model.Order(status=s.valid)
    db.save_doc(order)
    inbox.valid_order_prepare(db)
    db.refresh(order)
    assert order.status == s.ready


@with_quick_change_timeout
@pytest.mark.parametrize(('axis', 'specs'), [
    (None, [{}]),
    ({'test': ['a', 'b']}, [
        {'test': 'a'},
        {'test':'b'}
    ]),
], ids=['nospec', 'somespec'])
def test_ready_order_generate_tasks(db, axis, specs):
    order = model.Order(status='ready', axis=axis)
    db.save_doc(order)
    inbox.ready_order_generate_tasks(db)
    db.refresh(order)
    assert order.status == 'building'

    items = db._.bulk_save.call_args[0][0]
    saved_order = items.pop(0)

    assert saved_order._doc == order._doc
    for task, spec in zip(items, specs):

        assert task.spec == spec
