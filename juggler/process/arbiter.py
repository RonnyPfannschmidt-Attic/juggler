from juggler.process.procdir import ProcDir


class Arbiter(object):
    def __init__(self, db, basedir):
        self.db = db
        self.basedir = basedir

    def run(self, task):
        task.status = 'running'
        self.db.save_doc(task)  # XXX: might ressource conflict
        project_dir = self.basedir.join(task.project)
        procdir = ProcDir(self.db, project_dir, task)
        steps_for = procdir.find_steps()
        for step in steps_for:
            procdir.run(step)
