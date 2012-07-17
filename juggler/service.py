from .handlers.utils import watch_for
import time
import logbook

log = logbook.Logger('juggler', level='info')


class Juggler(object):
    def __init__(self, db, name, path=None):
        self.name = name
        self.db = db
        self.path = path

    def __repr__(self):
        return '<Juggler %r>' % self.db.dbname

    def watch_for(self, type, **kw):
        return watch_for(self.db, type, **kw)

    def all_current_docs_for(self, doc):
        #XXX: implement
        return []

    def save_doc(self, doc):
        self.db.save_doc(doc)

    def sleep(self):
        time.sleep(.5)

    def smart_watch(self, handler, **kw):
        #XXX: make a version that remembers since
        return handler(self, **kw)

    def refresh(self, doc):
        schema = type(doc)
        new_doc = self.real_db.get(doc._id, schema=schema)
        doc._doc = new_doc._doc

    def bulk_save(self, *k, **kw):
        self.db.bulk_save(*k, **kw)

    def get(self, *k, **kw):
        return self.db.get(*k, **kw)

    def run_task(self, task):
        #XXX: not cancelable yet
        assert self.path is not None
        from juggler.process.procdir import ProcDir
        procdir = ProcDir(self.db, self.path.join(task.project), task)
        steps = procdir.find_steps()
        assert steps
        task.status = 'building'
        log.debug('building {}', task._id)
        self.save_doc(task)
        for step in steps:
            log.debug('run {task._id} step {step.index}',
                     task=task, step=step)
            procdir.run(step)
        task.status = 'completed'
        log.info('completed {}', task._id)
        self.save_doc(task)
