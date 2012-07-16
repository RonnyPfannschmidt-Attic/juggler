import pytest
from mock import Mock
from juggler.process.baseproc import Proc


class ErrorProc(Proc):
    def fail(self):
        raise ValueError

    def create(self):
        self.spawn(self.fail)


def test_proc_wait_propagate_errors():
    proc = ErrorProc(Mock(), Mock())
    proc.queue.put(StopIteration)  # stop control
    pytest.raises(ValueError, proc.run)
