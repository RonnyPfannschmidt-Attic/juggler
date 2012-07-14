from __future__ import print_function
import py
import pytest
from juggler.process.subprocess import prepare_python


tasks = {
    'short': (
        r"print 'test'",
        r'test\n',
    ),
    'long': (
        r"print 'a\nb'",
        r"a\nb\n",
    ),
    'missing_final_newline': (
        r"print 'a',",
        "a ",
    ),
}


@pytest.mark.parametrize('task', sorted(tasks))
def test_lines_show(procdir, task):
    step = prepare_python(procdir, tasks[task][0], _id=task)
    assert step.task is not None
    procdir.db.save_doc(step)
    procdir.run(step)
    streams = list(procdir.find_streams(procdir.task._id))

    py.std.pprint.pprint(procdir.db.view('juggler/lines').all())
    py.std.pprint.pprint(procdir.db.view('juggler/streams', group=True).all())
    (stepid, name), = streams
    assert stepid == step._id
    print('stream', task, name)
    data = procdir.stream(stepid, name)
    print('data', data)
    assert len(data.splitlines()) <= 2
