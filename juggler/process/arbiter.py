

from juggler.model import
from glas_process.utils import steps_for


class Arbiter(object):
    def __init__(self, db, basedir):
        self.db = db
        self.basedir = basedir


    def run(self, task):
        project_dir = self.basedir.ensure(task.project, dir=1)
        procdir = Procdir(self.db, project_dir, task)


