import pytest
from mock import Mock
from juggler import workers
from juggler import model
from couchdbkit.exceptions import ResourceConflict


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


@pytest.mark.parametrize(('axis', 'specs'), [
    (None, [{}]),
    ({'test': ['a', 'b']}, [
        {'test': 'a'},
        {'test':'b'}
    ]),
], ids=['nospec', 'somespec'])
def test_ready_order_generate_tasks(axis, specs):
    db = Mock()
    order = model.Order(status='ready', axis=axis)
    watch_for = faked_watch_for(order)
    workers.ready_order_generate_tasks(db, watch_for)
    assert order.status == 'building'

    items = db.bulk_save.call_args[0][0]
    saved_order = items.pop(0)
    assert saved_order is order
    for task, spec in zip(items, specs):

        assert task.spec == spec


def test_new_task_generate_steps_programmatic_unimplemented():
    db = Mock()
    project = model.Project(computed_steps=True)
    db.get.return_value = project
    task = model.Task(status='new', project='blabla')
    watch_for = faked_watch_for(task)
    pytest.raises(
        NotImplementedError,
        workers.new_task_generate_steps,
        db, watch_for)


def test_new_task_generate_from_template():
    db = Mock()
    project = model.Project()
    db.get.return_value = project
    task = model.Task(status='new', project='blabla')
    watch_for = faked_watch_for(task)
    workers.new_task_generate_steps(db, watch_for)

    items = db.bulk_save.call_args[0][0]
    saved_task = items.pop(0)
    assert saved_task is task
    assert task.status == 'pending'
    #XXX: check items


@pytest.mark.parametrize('conflict', [False, True],
                         ids=['pass', 'conflict'])
def test_claim_pending_task(conflict):
    db = Mock()
    task = model.Task(status='pending', project='blabla')
    watch_for = faked_watch_for(task)

    if conflict:
        db.save_doc.side_effect = ResourceConflict()
    workers.claim_pending_task(db, watch_for, 'test')
    db.save_doc.assert_called_with(task)
