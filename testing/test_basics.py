from juggler import model


def test_make_project(juggler):
    project = model.Project(_id='test')
    trigger = model.Trigger(project='test', reason='test')
    juggler.store(trigger)
    juggler.store(build)
    print project
    print build
    assert build.status == 'prepare'
    juggler.shedule_jobs(build)
    assert build.status == 'building'

    jobs = juggler.db.view('jobs/all', schema=model.Job)
    job, = jobs
    assert job.spec == {}

    #XXX: hack
    job.status = 'completed'
    job.result = 'passed'
    juggler.store(job)

    print job

    build2 = model.Build(project='test',
                         axis={
                             '!patch': ['a', 'b', 'c'],
                         })
    juggler.shedule_jobs(build2)
    assert len(juggler.db.view('jobs/all')) == 4

