import time
from datetime import datetime
from reprtools import FormatRepr
import logbook
from juggler import async
from juggler.model import utils

log = logbook.Logger('Proc')


class Proc(object):

    __repr__ = FormatRepr('<Proc {step._id} - {step.status}>')

    def save_with_batch(self, doc):
        self.procdir.save_with_batch(doc)

    def save_step(self):
        self.procdir.db.save_doc(self.step)

    def __init__(self, procdir, step):
        self.procdir = procdir
        self.queue = async.Queue()
        self.greenlets = []
        self._control = None
        self.step = step

    def spawn(self, func, *k, **kw):
        res = async.spawn(func, *k, **kw)
        self.greenlets.append(res)
        return res

    def emit(self, event=None, **kw):
        log.debug('event emit {}', event or kw)
        self.queue.put(event or kw)
        time.sleep(0)

    def _store(self):
        iter = async.queue_iter(self.queue)
        for i, doc in enumerate(iter):
            log.debug('event store {}', doc)
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
        async.joinall(self.greenlets, raise_error=True)
        self.emit(StopIteration)
        self._control.join(timeout=5)
        #XXX: bad
        if not self._control.successful():
            raise self._control.exception

    def create(self):
        raise NotImplementedError

    def run(self):
        self.start()
        return self.wait()

    def kill(self):
        pass
