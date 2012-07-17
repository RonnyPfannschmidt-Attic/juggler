import contextlib
import threading
import py
import gevent

_BACKEND = py.std.os.environ.get("COUCHDBKIT_BACKEND", 'thread')


class StopInfo(threading.local):
    def __init__(self):
        self.current = False
        self.connection = []


class TimeoutError(Exception):
    pass


class ThreadExit(BaseException):
    pass


class StoppableThread(threading.Thread):
    stopped = False

    def kill(self, exc=ThreadExit()):
        self.stopped = exc

    def run(self):
        from juggler import async
        async.stop_info.current = self
        try:
            threading.Thread.run(self)
        except ThreadExit:
            pass


class SimpleModule(object):
    _BACKEND = _BACKEND
    stop_info = StopInfo()

    def __init__(self, oldmod):
        self.oldmod = oldmod

    def _magic_stop(self):
        current = self.stop_info.current
        if current and current.stopped:
            raise current.stopped


class ThreadAsyncModule(SimpleModule):
    sleep = staticmethod(py.std.time.sleep)

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
        self.sleep(time)
        self._magic_stop()
        tostop.kill(TimeoutError())

    @contextlib.contextmanager
    def Timeout(self, time):
        try:
            timer = self.spawn(
                self._timeout,
                self.stop_info.current,
                time)
            yield
        finally:
            timer.kill()
            # so late fireing doesnt confuse code after us
            self._magic_stop()

    def joinall(self, threads, **kw):
        print kw
        for t in threads:
            t.join(timeout=20)


class GeventAsyncModule(SimpleModule):
    spawn = staticmethod(gevent.spawn)
    sleep = staticmethod(gevent.sleep)
    joinall = staticmethod(gevent.joinall)
    Timeout = gevent.Timeout



lookup = {
    'thread': ThreadAsyncModule,
    'gevent': GeventAsyncModule,
}


import sys
current = sys.modules[__name__]
sys.modules[__name__] = lookup[_BACKEND](current)
