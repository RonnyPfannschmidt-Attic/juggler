import copy
from glas_process.subprocess import prepare_python, prepare_subprocess

def pytest_funcarg__procdir(request):
    procdir = request.getfuncargvalue('procdir')
    procdir._events = []
    def save(doc, **kw):
        newdoc = type(doc).wrap(copy.deepcopy(doc.to_json()))
        procdir._events.append(newdoc)
        type(procdir.db).save_doc(procdir.db, doc, **kw)
    procdir.db.save_doc = save
    return procdir


def check_events(procdir, checks):
    print procdir._events
    assert len(procdir._events) >= len(checks)
    for event, check in zip(procdir._events, checks):
        print event, check
        for attr, expected in zip(check[::2], check[1::2]):
            data = getattr(event, attr, None)
            print '  ', attr, expected,'==', data
            assert expected==data


def test_run_simple_process(procdir):
    procdir.path.ensure('somefile')
    step = prepare_subprocess(procdir, ['ls'], _id='the_ls')
    procdir.run(step)
    checks = [
        ('type', "juggler:step",
         'status', 'prepared'),
        ('type', "juggler:step",
         'status', "running"),
        ('line', 'somefile\n'),
        ('returncode', 0),
        ('type', "juggler:step",
         'status', "complete"),
    ]
    check_events(procdir, checks)

def test_simple_process_failure(procdir):
    step = prepare_subprocess(procdir, ['false'])
    procdir.run(step)
    checks = [
        ('type', "juggler:step",
         'status', 'prepared'),
        ('type', "juggler:step",
         'status', "running"),
        ('returncode', 1),
        ('type', "juggler:step",
         'status', "failed"),
    ]
    check_events(procdir, checks)

def test_cat_process(procdir):
    doc = prepare_subprocess(procdir,
                        ['head', '-n', '30', '/etc/services'],
                        _id='cat')
    procdir.run(doc)
    for event in procdir._events:
        if hasattr(event, 'lineno'):
            print event, event.line.rstrip()
        else:
            print event

def test_python(procdir):
    doc = prepare_python(procdir, 'print 1\n')
    procdir.run(doc)
    checks = [
        ('type', "juggler:step",
         'status', 'prepared'),
        ('type', "juggler:step",
         'status', "running"),
        ('line', '1\n'),
        ('returncode', 0),
        ('type', "juggler:step",
         'status', "complete"),
    ]
    check_events(procdir, checks)


