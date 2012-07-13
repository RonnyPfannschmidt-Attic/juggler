from __future__ import print_function, absolute_import

import os
import fcntl
import errno
import sys

import subprocess
import gevent
from gevent.socket import wait_read
from .baseproc import Proc, makestep


def prepare_python(proc, script, _id=None):
    return makestep(
        proc, _id,
        variant='python',
        steper='popen',
        args=['python', '-'],
        stdin=script,
    )


def prepare_subprocess(proc, cmd, _id=None):
    return makestep(
        proc, _id,
        variant='subprocess',
        steper='popen',
        args=[str(x) for x in cmd],
        stdin=None,
    )


class SubProcessProc(Proc):

    def create(self):
        self.step.status = 'running'
        self.save_step()
        self.popen = start_subprocess(self)


def stream_line_iter(fp):
    fcntl.fcntl(fp, fcntl.F_SETFL, os.O_NONBLOCK)  # make the file nonblocking
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
        gevent.sleep(.1)
        code = proc.poll()
        if code is not None:
            q.put({'returncode': code})
            return


def _joinall(queue, *greenlets):
    gevent.joinall(greenlets)
    queue.put(StopIteration)


def start_subprocess(proc):
    step = proc.step
    popen = subprocess.Popen(
        step.args,
        cwd=str(proc.procdir.path),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    q = proc.queue
    out = gevent.spawn(_stream_reader, popen, 'stdout', q)
    err = gevent.spawn(_stream_reader, popen, 'stderr', q)
    ret = gevent.spawn(_exit_poller, popen, q)
    gevent.spawn(_joinall, q, out, err, ret)

    stdin = getattr(step, 'stdin', None)
    if stdin is not None:
        popen.stdin.write(stdin)
    popen.stdin.close()
    return popen
