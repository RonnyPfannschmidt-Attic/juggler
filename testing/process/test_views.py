from __future__ import print_function
from glas_process.subprocess import prepare_subprocess

def test_lines_show(procdir):
    procdir.path.ensure('test')
    ls = prepare_subprocess(procdir,['ls'], _id='ls:short')
    ls_long = prepare_subprocess(procdir, ['ls', '-l'], _id='ls:long')
    procdir.run(ls)
    procdir.run(ls_long)

    for task in ('ls:short', 'ls:long'):
        print('task', task)
        streams = procdir.find_streams(task)
        for step, stream in streams:
            print(' ', step, stream)
            data = procdir.stream(step, stream)
            print('   ', repr(data))
            assert len(data.splitlines()) <= 2

