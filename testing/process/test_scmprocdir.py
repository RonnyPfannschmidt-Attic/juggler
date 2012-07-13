import py
import pytest

import socket
import gevent

from glas_process.baseproc import makestep


try:
    socket.gethostbyname('bitbucket.org')
    net = True
except socket.gaierror:
    net = False

paths = [
    py.path.local(__file__).dirpath().dirpath().strpath,
    'http://bitbucket.org/RonnyPfannschmidt/hgdistver',
]


@pytest.mark.no_create
@pytest.mark.parametrize('path', paths,)
def test_simple_clone(procdir, path):
    if str(path).startswith('http') and not net:
        pytest.skip('no net')
    assert not procdir.path.check()

    step = makestep(
        procdir, None,
        steper='scm',
        repo=path,
        branch=None,
        intent='create_or_pull',
    )

    procdir.run(step)
    gevent.sleep(0)
    assert procdir.path.check()
    step_repeat = makestep(
        procdir, None,
        steper='scm',
        repo=path,
        branch=None,
        intent='create_or_pull',
    )
    procdir.run(step_repeat)

    step_update = makestep(
        procdir, None,
        steper='scm',
        repo=path,
        branch=None,
        intent='update_wd',
    )
    procdir.run(step_update)

