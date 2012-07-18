from __future__ import absolute_import

import os
import errno
import sys

import subprocess
from .baseproc import Proc

from juggler import async


def python_template(script):
    return dict(
        variant='python',
        steper='popen',
        args=['python', '-'],
        stdin=script,
        env={},
    )


def subprocess_template(cmd):
    return dict(
        variant='subprocess',
        steper='popen',
        args=[str(x) for x in cmd],
        stdin=None,
        env={},
    )


class SubProcessProc(Proc):

    def create(self):
        self.step.status = 'running'
        self.save_step()
        self.popen = start_subprocess(self)


def stream_line_iter_gevent(fp):
    import fcntl
    from gevent.socket import wait_read
    # make the file nonblocking
    fcntl.fcntl(fp, fcntl.F_SETFL, os.O_NONBLOCK)
    remainder = ''
    while True:
        try:
            chunk = fp.read(1024)
            if not chunk:
                if remainder:
                    yield remainder
                return

        except IOError:
            ex = sys.exc_info()[1]
            if ex[0] != errno.EAGAIN:
                raise
        else:
            data = remainder + chunk
            lines = data.splitlines(1)
            if lines[-1][-1] != '\n':
                remainder = lines.pop()
            else:
                remainder = ''
            for line in lines:
                yield line
            remainder  # XXX: pyflakes
        wait_read(fp.fileno())


def stream_line_iter(fp):
    if async._BACKEND == 'gevent':
        return stream_line_iter_gevent(fp)
    elif async._BACKEND == 'thread':
        return iter(fp)


def _stream_reader(proc, stream, queue):
    fp = getattr(proc, stream)

    for lineno, line in enumerate(stream_line_iter(fp)):
        queue.put({
            'stream': stream,
            'lineno': lineno,
            'line': line,
        })


def _exit_poller(proc, q):
    while True:
        async.sleep(.1)
        code = proc.poll()
        if code is not None:
            q.put({'returncode': code})
            return


def _joinall(queue, *greenlets):
    async.joinall(greenlets)
    queue.put(StopIteration)


def start_subprocess(proc):
    step = proc.step
    proc.procdir.path.ensure(dir=1)
    popen = subprocess.Popen(
        #XXX: unittest for that
        [str(x) for x in step.args],
        cwd=str(proc.procdir.path),
        env=step.env or {},
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    q = proc.queue
    out = async.spawn(_stream_reader, popen, 'stdout', q)
    err = async.spawn(_stream_reader, popen, 'stderr', q)
    ret = async.spawn(_exit_poller, popen, q)
    async.spawn(_joinall, q, out, err, ret)

    stdin = getattr(step, 'stdin', None)
    if stdin is not None:
        popen.stdin.write(stdin)
    popen.stdin.close()
    return popen
