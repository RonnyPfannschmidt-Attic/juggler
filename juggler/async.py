import time
import threading
import os
import select

_BACKEND = os.environ.get("COUCHDBKIT_BACKEND", 'thread')


class StopInfo(threading.local):
    def __init__(self):
        self.current = False
        self.connection = []


stop_info = StopInfo()


def _magic_stop():
    current = stop_info.current
    if current and current.stopped:
        raise current.stopped


class TimeoutError(Exception):
    pass


class ThreadExit(BaseException):
    pass


class StoppableThread(threading.Thread):
    stopped = False
    exception = None

    def successful(self):
        return self.exception is None

    def kill(self, exc=ThreadExit()):
        self.stopped = exc

    def run(self):
        stop_info.current = self
        try:
            threading.Thread.run(self)
        except ThreadExit:
            pass
        except Exception as e:
            self.exception = e
            raise


class ThreadAsyncModule(object):
    from Queue import Queue, Empty
    Queue, Empty  # silence pyflakes

    def wait_read(self, fd):
        r = None
        while not r:
            r, _, _ = select.select([fd], [], [], 0.2)
            _magic_stop()

    def sleep(self, seconds):
        time.sleep(seconds)
        _magic_stop()

    def spawn(self, func, *args, **kwargs):
        thread = StoppableThread(
            target=func,
            args=args,
            kwargs=kwargs,
        )
        thread.start()
        return thread

    def joinall(self, threads, raise_error=False):
        #XXX: timeout
        for thread in threads:
            thread.join()
            if raise_error and thread.exception:
                    raise thread.exception

    def queue_iter(self, queue):
        while True:
            try:
                item = queue.get(timeout=0.5)
            except self.Empty:
                _magic_stop()
            else:
                if item is StopIteration:
                    break
                else:
                    yield item


try:
    import gevent
except ImportError:
    GeventAsyncModule = None
else:
    class GeventAsyncModule(object):
        from gevent.queue import Queue
        Queue  # silence pytest
        from gevent.socket import wait_read
        wait_read = staticmethod(wait_read)
        spawn = staticmethod(gevent.spawn)
        sleep = staticmethod(gevent.sleep)
        joinall = staticmethod(gevent.joinall)
        queue_iter = staticmethod(iter)

lookup = {
    'thread': ThreadAsyncModule,
    'gevent': GeventAsyncModule,
}

current = lookup[_BACKEND]()

spawn = current.spawn
sleep = current.sleep
joinall = current.joinall
Queue = current.Queue
queue_iter = current.queue_iter
wait_read = current.wait_read
