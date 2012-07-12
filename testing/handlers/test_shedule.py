import pytest
from juggler import workers, model


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
    project = model.Project(steps=[])
    db._.get.return_value = project
    task = model.Task(status='new', project='blabla')
    db.save_doc(task)
    workers.new_task_generate_steps(db)
    items = db._.bulk_save.call_args[0][0]
    saved_task = items.pop(0)
    db.refresh(task)
    assert saved_task.status == task.status
    assert task.status == 'pending'
    #XXX: check items


def test_approve_claimed_task_simple(db):
    task = model.Task(status='claiming', owner='test')
    db.save_doc(task)
    workers.approve_claimed_task(db)
    db.refresh(task)
    assert task.status == 'claimed'


@pytest.mark.xfail(run=False, reason='tricky')
def test_approve_claimed_task_two_exist():
    pass


@pytest.mark.xfail(run=False, reason='tricky')
def test_approve_claimed_tasks_stat_conflict_solution():
    pass
