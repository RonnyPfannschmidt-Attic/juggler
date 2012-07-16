from datetime import datetime

from reprtools import FormatRepr

import gevent
from gevent.queue import Queue

from juggler.model import utils


class Proc(object):

    __repr__ = FormatRepr('<Proc {step._id} - {step.status}>')

    def save_with_batch(self, doc):
        self.procdir.save_with_batch(doc)

    def save_step(self):
        self.procdir.db.save_doc(self.step)

    def __init__(self, procdir, step):
        self.procdir = procdir
        self.queue = Queue()
        self.greenlets = []
        self._control = None
        self.step = step

    def spawn(self, func, *k, **kw):
        res = gevent.spawn(func, *k, **kw)
        self.greenlets.append(res)
        return res

    def emit(self, event=None, **kw):
        self.queue.put(event or kw)

    def _store(self):
        for i, doc in enumerate(self.queue):
            doc = utils.complete_event(doc, i, self.step, self.procdir.task)

            self.save_with_batch(doc)
            returncode = getattr(doc, 'returncode', None)
            if returncode is not None and self.step is not None:
                self.finish_step('complete' if returncode == 0 else 'failed')

    def finish_step(self, newstate):
        self.step.status = newstate
        self.step.finished = datetime.now()
        self.save_step()

    def start(self):
        if self._control is None:
            self.create()
            self._control = self.spawn(self._store)

    def wait(self):
        self.start()
        self._control.join()
        gevent.joinall(self.greenlets, raise_error=True)
        if not self._control.successful():
            raise self._control.exception

    def create(self):
        raise NotImplementedError

    def run(self):
        self.start()
        return self.wait()

    def kill(self):
        pass
