import anyvc
from .baseproc import Proc
from logbook import Logger
log = Logger('juggler scm')


class ScmProc(Proc):

    def create_or_pull(self):
        "clone or pull (as in hg pull)"
        target = self.procdir.path
        repo = self.step.repo
        log.debug("clone or pull {.task}", self.step)
        if not target.check(dir=1):
            self.emit(start='clone')
            self.wd = anyvc.workdir.clone(repo, target)
            self.emit(end='clone')
        else:
            self.emit(start='pull')
            self.wd = anyvc.workdir.open(target)
            self.wd.repository.pull(repo)
            self.emit(end='pull')

    def reset_state(self):
        "undo patches, purge workdir if exists"

    def update_wd(self):
        "update to target branch/rev"
        log.debug('update wd {}', self.procdir.path)
        self.wd = anyvc.workdir.open(self.procdir.path)
        self.wd.update(revision=getattr(self.step, 'revision', None))

    def maybe_create_mq(self):
        "create a hg patch queue for the given patches"

    def maybe_apply_patches(self):
        "push patches up to the required patch"

    def _run_intent(self):
        intent = getattr(self, self.step.intent)
        intent()
        self.emit(StopIteration)

    def create(self):
        self.spawn(self._run_intent)
