from juggler import model



def test_make_project(juggler):
    project = model.Project(id='test')
    build = model.Build(project='test', reason='test')
    juggler.store(project)
    juggler.store(build)
    print project
    print build
    juggler.shedule_jobs(build)
    jobs = juggler.db.view('jobs/all', schema=model.Job)
    job, = jobs


    #XXX: hack
    job.status = 'completed'
    job.result = 'passed'
    juggler.store(job)

    print job
    assert 0

