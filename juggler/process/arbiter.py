from juggler.model import Step
from juggler.process.utils import steps_for
from juggler.process.procdir import Procdir


class Arbiter(object):
    def __init__(self, db, basedir):
        self.db = db
        self.basedir = basedir

    def run(self, task):
        Step
        steps_for
        project_dir = self.basedir.ensure(task.project, dir=1)
        procdir = Procdir(self.db, project_dir, task)
        for step in steps_for:
            procdir.run(step)
