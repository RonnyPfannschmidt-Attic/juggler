import pytest
from juggler import model
from juggler.handlers import shedule
from testing import with_quick_change_timeout


@with_quick_change_timeout
def test_new_task_generate_steps_programmatic_unimplemented(db):
    project = model.Project(computed_steps=True)
    db._.get.return_value = project
    task = model.Task(status='new', project='blabla')
    db.save_doc(task)
    pytest.raises(
        NotImplementedError,
        shedule.new_task_generate_steps,
        db)


@with_quick_change_timeout
def test_new_task_generate_from_template(db):
    project = model.Project(steps=[])
    db._.get.return_value = project
    task = model.Task(status='new', project='blabla')
    db.save_doc(task)
    shedule.new_task_generate_steps(db)
    items = db._.bulk_save.call_args[0][0]
    saved_task = items.pop(0)
    db.refresh(task)
    assert saved_task.status == task.status
    assert task.status == 'pending'
    #XXX: check items


@with_quick_change_timeout
def test_approve_claimed_task_simple(db):
    task = model.Task(status='claiming', owner='test')
    db.save_doc(task)
    shedule.approve_claimed_task(db)
    db.refresh(task)
    assert task.status == 'claimed'


@with_quick_change_timeout
@pytest.mark.xfail(run=False, reason='tricky')
def test_approve_claimed_task_two_exist():
    pass


@with_quick_change_timeout
@pytest.mark.xfail(run=False, reason='tricky')
def test_approve_claimed_tasks_stat_conflict_solution():
    pass
