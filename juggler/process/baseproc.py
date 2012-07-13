from datetime import datetime

import gevent
from gevent.queue import Queue

from juggler.model import Step, Event


def makestep(procdir, _id, steper, **kw):
    return Step(
        _id=procdir.get_id(steper, _id),
        status='prepared',
        steper=steper,
        task=procdir.task._id,
        **kw)


class Proc(object):

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
        self.save_step()

    def spawn(self, func, *k, **kw):
        res = gevent.spawn(func, *k, **kw)
        self.greenlets.append(res)
        return res

    def emit(self, event=None, **kw):
        self.queue.put(event or kw)

    def _store(self):
        for i, doc in enumerate(self.queue):
            if isinstance(doc, dict):
                doc = Event(**doc)
            if not doc._id:
                doc._id = '%s:%s' % (self.step._id, i)
            if not doc.step:
                doc.step = self.step._id
            doc.index = i

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
        gevent.joinall(self.greenlets)

    def create(self):
        raise NotImplementedError

    def run(self):
        self.start()
        return self.wait()

    def kill(self):
        pass
