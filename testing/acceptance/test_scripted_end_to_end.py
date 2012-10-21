import py
import pytest
from juggler import async
from juggler.service import Juggler
from juggler.handlers import inbox, manage, slave
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
    manage.new_task_generate_steps(juggler)

    slave.claim_pending_task(juggler, owner=juggler)

    manage.approve_claimed_task(juggler)
    slave.run_one_claimed_task(juggler,
                               owner=juggler.name,
                               run=juggler.run_task)


@pytest.mark.changes_extra(timeout=300)
@pytest.mark.parametrize('axis', [
    {},
    {'test': [1, 2, 3, 4, 5, 6]},
    {'test': [1, 2, 3, 4, 5, 6], 'test2':[1, 2, 3, 4, 5, 6]},
], ids=['small', 'medium', 'large'])
def test_spawned_parts_2_simple_worker(juggler, axis, tmpdir):
    slave1_juggler = Juggler(juggler.db, 'slave1', tmpdir.join('slave1'))
    slave2_juggler = Juggler(juggler.db, 'slave2', tmpdir.join('slave2'))
    slave1 = async.spawn(simple_slave.simple, slave1_juggler)
    slave2 = async.spawn(simple_slave.simple, slave2_juggler)
    slave1._Thread__name = 'slave 1'
    slave2._Thread__name = 'slave 2'
    master = async.spawn(simple_master.simple_master, juggler)
    master._Thread__name = 'master'

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
    async.sleep(0.1)

    def wait_for_completion(juggler):
        while True:
            async.sleep(0.5)
            items = juggler.db.view(
                'juggler/stm',
                startkey=['juggler:task'],
                endkey=['juggler:task', {}],
                reduce=False,
            ).all()
            if not items:
                continue
            counter = py.std.collections.Counter(
                ' '.join(item['key']) for item in items
            )
            py.std.pprint.pprint(counter)
            if counter[u'juggler:task completed'] == len(items):
                break
    completion = async.spawn(wait_for_completion, juggler)
    completion._Thread__name = 'completion'
    try:
        completion.join(timeout=60)  # 2 min
    finally:
        import threading
        for thread in threading.enumerate():
            thread._Verbose__verbose = True
        completion.kill()
        slave1.kill()
        slave2.kill()
        master.kill()
    #XXX: check all tasks for completion status
    #ask = juggler.get(step.task, schema=Task)
    #assert task.project == project._id
    async.joinall([master, slave1, slave2, completion], raise_error=True)
