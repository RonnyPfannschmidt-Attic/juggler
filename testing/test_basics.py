import gevent
import pytest
from juggler import model


def test_make_project(couchdb, juggler):
    pytest.skip('fuu')
    project = model.Project(_id='test')
    trigger = model.Trigger(project='test', reason='test')
    couchdb.save_doc(project)
    couchdb.save_doc(trigger)
    print project
    print trigger
    assert trigger.status == 'prepare'
    juggler.start()
    trigger.status = 'ready'
    couchdb.save_doc(trigger)
    gevent.sleep(.2)  # let the driver handle
    trigger_newstate = couchdb.get(trigger.id)
    assert trigger_newstate.status == 'building'

    jobs = juggler.db.view('jobs/all', schema=model.Job)
    job, = jobs
    assert job.spec == {}

    #XXX: hack
    job.status = 'completed'
    job.result = 'passed'
    juggler.store(job)

    print job
    pass
    build2 = model.Build(project='test',
                         axis={
                             '!patch': ['a', 'b', 'c'],
                         })
    juggler.shedule_jobs(build2)
    assert len(juggler.db.view('jobs/all')) == 4
