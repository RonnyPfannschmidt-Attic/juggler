import py
import pytest

import socket
from juggler import async

from juggler.model import Step


try:
    socket.gethostbyname('bitbucket.org')
    net = True
except socket.gaierror:
    net = False

paths = [
    py.path.local(__file__).join('../../..').strpath,
    'http://bitbucket.org/RonnyPfannschmidt/hgdistver',
]


@pytest.mark.no_create
@pytest.mark.parametrize('path', paths,)
def test_simple_clone(procdir, path):
    if str(path).startswith('http') and not net:
        pytest.skip('no net')
    assert not procdir.path.check()

    step = Step(
        _id='clone',
        task=procdir.task._id,
        steper='scm',
        repo=path,
        branch=None,
        intent='create_or_pull',
    )

    procdir.run(step)
    async.sleep(0)
    assert procdir.path.check()
    step_repeat = Step(
        _id='clone_2',
        task=procdir.task._id,
        steper='scm',
        repo=path,
        branch=None,
        intent='create_or_pull',
    )
    procdir.run(step_repeat)

    step_update = Step(
        _id='update',
        task=procdir.task._id,
        steper='scm',
        repo=path,
        branch=None,
        intent='update_wd',
    )
    procdir.run(step_update)


@pytest.mark.xfail(run=False, reason='not implemented')
def test_simple_clone_failures():
    pass
