import sys
from juggler import async
import subprocess
from juggler.process.subprocess import stream_line_iter

cases = [
    ('bash', ['bash', '-c', 'echo 1;sleep 3;echo 2']),
    ('python', [
        sys.executable, '-u', '-c',
        'print 1;import sys;sys.stdout.flush();import time;time.sleep(3);print 2'
    ])
]



def test_line_stream_noblock():
    p = subprocess.Popen([
        sys.executable, '-u', '-c',
                                   # wtf why
        'print 1;import sys;sys.stdout.flush();import time;time.sleep(3);print 2'
    ], stdout=subprocess.PIPE)
    q = async.Queue()
    def work():
        for line in stream_line_iter(p.stdout):
            q.put(line)
    proc = async.spawn(work)
    try:
        line1 = q.get(timeout=0.5)
        line2 = q.get(timeout=3)
    finally:
        proc.kill()
        proc.join()
