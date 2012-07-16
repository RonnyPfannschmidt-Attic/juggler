import pytest
from couchdbkit.exceptions import ResourceConflict
from juggler import model
from juggler.handlers import slave
from testing import with_quick_change_timeout


@with_quick_change_timeout
@pytest.mark.parametrize('conflict', [False, True],
                         ids=['pass', 'conflict'])
def test_claim_pending_task(db, conflict):
    task = model.Task(status='pending', project='blabla')
    db.save_doc(task)
    if conflict:
        db._.save_doc.side_effect = ResourceConflict()

    class owner:
        name = 'test'

    result = slave.claim_pending_task(db, owner=owner)
    db.refresh(task)
    if not conflict:
        assert task.owner == 'test'
        assert task.status == 'claiming'
        assert result._id == task._id


@with_quick_change_timeout
def test_run_one_claimed_task(db):
    task = model.Task(_id='claim', owner='o', status='claimed')
    db.save_doc(task)

    def run(given):
        assert given._id == task._id

    slave.run_one_claimed_task(db, owner='o', run=run)
