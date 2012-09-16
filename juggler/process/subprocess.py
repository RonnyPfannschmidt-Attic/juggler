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


def stream_chunk_iter(fp, size=1024):
    import fcntl
    # make the file nonblocking
    fcntl.fcntl(fp, fcntl.F_SETFL, os.O_NONBLOCK)
    while True:
        async.wait_read(fp)
        try:
            chunk = fp.read(size)
            if not chunk:
                break
            yield chunk
        except IOError:
            ex = sys.exc_info()[1]
            if ex[0] != errno.EAGAIN:
                raise


def stream_line_iter(fp):
    remainder = ''
    for chunk in stream_chunk_iter(fp):
        data = remainder + chunk
        lines = data.splitlines(1)
        if lines[-1][-1] != '\n':
            remainder = lines.pop()
        else:
            remainder = ''
        for line in lines:
            yield line
        remainder  # XXX: pyflakes


def _stream_reader(proc, stream, emit):
    fp = getattr(proc, stream)

    for lineno, line in enumerate(stream_line_iter(fp)):
        emit(
            stream=stream,
            lineno=lineno,
            line=line,
        )


def _exit_poller(proc, emit):
    while True:
        async.sleep(.1)
        code = proc.poll()
        if code is not None:
            emit(returncode=code)
            return


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
    proc.spawn(_stream_reader, popen, 'stdout', proc.emit)
    proc.spawn(_stream_reader, popen, 'stderr', proc.emit)
    proc.spawn(_exit_poller, popen, proc.emit)

    stdin = getattr(step, 'stdin', None)
    if stdin is not None:
        popen.stdin.write(stdin)
    popen.stdin.close()
    return popen
