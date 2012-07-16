from __future__ import print_function
import py
import pytest
from juggler.process.subprocess import python_template
from juggler.model import Step

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
    step = Step(_id=task, task=task,
                **python_template(tasks[task][0]))
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


def test_find_steps(procdir):
    step = Step(task=procdir.task._id)
    procdir.db.save_doc(step)
    found = procdir.find_steps()
    assert found[0]._id == step._id
    assert len(found) == 1
