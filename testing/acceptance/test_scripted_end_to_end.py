from mock import Mock
import pytest
from juggler.handlers import inbox, shedule, slave
from juggler.model import Project, Order


@pytest.mark.changes_extra(timeout=1)
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

    slave.claim_pending_task(juggler)

    shedule.approve_claimed_task(juggler)

    mock = Mock()
    mock.name = juggler.name
    mock.once = False

    def side_effect(step):
        if mock.once:
            raise ValueError(step)
        mock.once = True
        print step
        assert step.steper == 'python'

    mock.run.side_effect = side_effect
    slave.run_one_claimed_task(juggler, owner=mock)
