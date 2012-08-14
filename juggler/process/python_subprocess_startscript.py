#!/usr/bin/python
import sys


class FlushFile(object):
    """Write-only flushing wrapper for file-type objects."""

    def __init__(self, f):
        self.f = f

    def write(self, x):
        self.f.write(x)
        self.f.flush()

# Replace stdout with an automatically flushing version
sys.stdout = FlushFile(sys.__stdout__)

script = sys.stdin.read()

code = compile(script, '<script>')

exec(code)
