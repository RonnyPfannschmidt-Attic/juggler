import contextlib
import threading
import py
import gevent

_BACKEND = py.std.os.environ.get("COUCHDBKIT_BACKEND", 'thread')


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

    def sleep(self, time):
        py.std.time.sleep(time)
        _magic_stop()

    def spawn(self, func, *args, **kwargs):
        thread = StoppableThread(
            target=func,
            args=args,
            kwargs=kwargs,
        )
        thread.start()
        return thread

    def _timeout(self, tostop, time):
        #XXX: incremental loop to make this joinable
        for i in range(100):
            self.sleep(time / 100.0)
            _magic_stop()
        tostop.kill(TimeoutError())

    @contextlib.contextmanager
    def Timeout(self, time):
        timer = self.spawn(
            self._timeout,
            stop_info.current,
            time)
        try:
            yield
        finally:
            timer.kill()
            # so late fireing doesnt confuse code after us
            _magic_stop()

    def joinall(self, threads, raise_error=False):
        for t in threads:
            t.join(timeout=1)
            if raise_error and t.exception:
                raise t.exception

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


class GeventAsyncModule(object):
    from gevent.queue import Queue
    Queue  # silence pytest
    spawn = staticmethod(gevent.spawn)
    sleep = staticmethod(gevent.sleep)
    joinall = staticmethod(gevent.joinall)
    Timeout = gevent.Timeout
    queue_iter = staticmethod(iter)


lookup = {
    'thread': ThreadAsyncModule,
    'gevent': GeventAsyncModule,
}

current = lookup[_BACKEND]()

spawn = current.spawn
sleep = current.sleep
joinall = current.joinall
Timeout = current.Timeout
Queue = current.Queue
queue_iter = current.queue_iter
