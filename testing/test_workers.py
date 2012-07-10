import pytest
from mock import Mock
from juggler import workers
from juggler import model
from couchdbkit.exceptions import ResourceConflict


def pytest_generate_tests(metafunc):
    if 'db' in metafunc.funcargnames:
        #l = ['direct', 'mocked']
        l = ['mocked']
        metafunc.parametrize('db', l, ids=l, indirect=True)


def faked_watch_for(result, info=None):
    def faked_watch_for(type, **kw):
        assert isinstance(result, type)
        for k, v in kw.items():
            assert getattr(result, k) == v

        return result, info
    return faked_watch_for


class FakedDatabase(object):
    def __init__(self, real_db=None):
        self.real_db = real_db
        if real_db is not None:
            self.db = Mock(wraps=real_db)
        else:
            self.db = Mock()
        self._ = self.db

    def get(self, *k, **kw):
        return self.db.get(*k, **kw)

    def save_doc(self, doc):
        #XXX: hack
        if 'watch_for' not in vars(self) and self.real_db is None:
            self.watch_for = faked_watch_for(doc)
        else:
            self.db.save_doc(doc)

    def bulk_save(self, *k, **kw):
        self.db.bulk_save(*k, **kw)


def pytest_funcarg__db(request):
    if request.param == 'direct':
        db = request.getfuncargvalue('couchdb')
    else:
        db = None
    return FakedDatabase(db)


def test_inbox_simple_validate(db):
    #XXX: test a invalid case
    order = model.Order(status='received')
    db.save_doc(order)
    workers.inbox_validate(db)
    assert order.status == 'valid'
    db.db.save_doc.assert_called_with(order)


def test_valid_order_simple_ready(db):
    order = model.Order(status='valid')
    db.save_doc(order)
    workers.valid_order_prepare(db)
    assert order.status == 'ready'
    db._.save_doc.assert_called_with(order)


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
    workers.ready_order_generate_tasks(db)
    assert order.status == 'building'

    items = db._.bulk_save.call_args[0][0]
    saved_order = items.pop(0)
    assert saved_order is order
    for task, spec in zip(items, specs):

        assert task.spec == spec


def test_new_task_generate_steps_programmatic_unimplemented(db):
    project = model.Project(computed_steps=True)
    db._.get.return_value = project
    task = model.Task(status='new', project='blabla')
    db.save_doc(task)
    pytest.raises(
        NotImplementedError,
        workers.new_task_generate_steps,
        db)


def test_new_task_generate_from_template(db):
    project = model.Project()
    db._.get.return_value = project
    task = model.Task(status='new', project='blabla')
    db.save_doc(task)
    workers.new_task_generate_steps(db)
    items = db._.bulk_save.call_args[0][0]
    saved_task = items.pop(0)
    assert saved_task is task
    assert task.status == 'pending'
    #XXX: check items


@pytest.mark.parametrize('conflict', [False, True],
                         ids=['pass', 'conflict'])
def test_claim_pending_task(db, conflict):
    task = model.Task(status='pending', project='blabla')
    db.save_doc(task)
    if conflict:
        db._.save_doc.side_effect = ResourceConflict()
    workers.claim_pending_task(db, 'test')
    db._.save_doc.assert_called_with(task)
    assert task.owner == 'test'
    assert task.status == 'claiming'
