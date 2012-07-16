import pytest
import gevent
from juggler.handlers import inbox, shedule, slave
from juggler.model import Project, Order
from juggler.process.subprocess import python_template
from testing import with_quick_change_timeout
from juggler import simple_slave, simple_master


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


@pytest.mark.changes_extra(timeout=3000)
@pytest.mark.parametrize('axis', [
    {},
    {'test': [1, 2, 3, 4, 5, 6]}
], ids=['small', 'medium'])
def test_spawned_parts_simple_worker(juggler, axis):
    slave = gevent.spawn(simple_slave.simple, juggler)
    master = gevent.spawn(simple_master.simple_master, juggler)

    project = Project(_id='project', steps=[
        python_template('print "hi"'),
    ])
    order = Order(
        _id='order',
        status='received',
        project='project',
        axis=axis)

    juggler.save_doc(project)
    juggler.save_doc(order)
    gevent.sleep(0.1)

    def wait_for_completion():
        with gevent.Timeout(10):
            while True:
                gevent.sleep(0.5)
                items = juggler.db.view(
                    'juggler/stm',
                    startkey=['juggler:task'],
                    endkey=['juggler:task', {}],
                ).all()
                print '-' * 10
                for item in items:
                    print item['key'], item['id']
                if not items:
                    continue
                if all(item['key'][1] == 'complete' for item in items):
                    break
    completion = gevent.spawn(wait_for_completion)

    #XXX: check all tasks for completion status
    #ask = juggler.get(step.task, schema=Task)
    #assert task.project == project._id
    slave.kill()
    master.kill()
    gevent.joinall([master, slave, completion], raise_error=True)
