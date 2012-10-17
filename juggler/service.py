from .handlers.utils import watch_for
import logbook
from couchdbkit import ResourceConflict
from juggler.model import states as s

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
        schema = type(doc)
        items = self.db.get(doc._id, open_revs='all')
        docs = [item[u'ok'] for item in items if u'ok' in item]
        log.debug('versions {}', docs)
        if not isinstance(doc, dict):
            docs = [schema.wrap(item) for item in docs]
        return docs

    def save_doc(self, doc):
        self.db.save_doc(doc)

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
        task.status = s.building
        try:
            self.save_doc(task)
            log.debug('building {}', task._id)
        except ResourceConflict:
            #XXX: test for this case
            log.error('building {} failed due to db conflict', task._id)
            return
        for step in steps:
            log.debug(
                'run {task._id} step {step.index}',
                task=task, step=step)
            procdir.run(step)
            #XXX: test for break
            if step.status != s.complete:
                break
        # a task ends with the state of the last step finished
        # which may be completed, failed or canceled
        task.status = step.status
        log.info('completed {}', task._id)
        self.save_doc(task)
