from juggler.handlers import inbox, shedule, slave
from juggler.model import Project, Order
from juggler.process.subprocess import python_template
from testing import with_quick_change_timeout


@with_quick_change_timeout
def test_scripted_end_to_end(juggler, tmpdir):
    juggler.path = tmpdir
    project = Project(_id='project', steps=[
        python_template('print "hi"'),
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
    slave.run_one_claimed_task(juggler,
                               owner=juggler.name,
                               run=juggler.run_task)

    assert 0
