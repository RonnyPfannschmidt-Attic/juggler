from juggler.handlers import inbox, shedule, slave
from juggler.model import Project, Order

from testing import with_quick_change_timeout


@with_quick_change_timeout
def test_scripted_end_to_end(juggler):
    project = Project(_id='project', steps=[
        {'steper': 'python', 'input':'print "hi"'},
    ])
    order = Order(project='project', _id='order', status='received')

    juggler.db.save_doc(project)
    juggler.db.save_doc(order)

    inbox.order_validate(juggler)
    inbox.valid_order_prepare(juggler)
    inbox.ready_order_generate_tasks(juggler)
    shedule.new_task_generate_steps(juggler)

    slave.claim_pending_task(juggler, owner=juggler)

    shedule.approve_claimed_task(juggler)

    def run_task(task):
        print task
        assert not run_task.once
        run_task.once = True
        assert task.project == project._id
        assert task.order == order._id

    run_task.once = False

    slave.run_one_claimed_task(juggler, owner=juggler.name, run=run_task)
