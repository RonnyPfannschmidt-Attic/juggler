from collections import Counter

class ProcDir(object):
    scminfo = None

    def __init__(self, db, path, task):
        self.db = db
        self.path = path
        self.task = task
        self._idcounter = Counter()

    def get_id(self, steper, given=None):
        if given is not None:
            return given
        current = self._idcounter[steper]
        self._idcounter.update([steper])
        print current, steper
        suffix = '_%s' % current if current else ""
        return '%s:%s%s' % (self.task._id, steper, suffix)

    def save_with_batch(self, doc):
        return self.db.save_doc(doc, batch='ok')

    def find_streams(self, task):
        res = self.db.view('glas_process/streams', group='true',
                           startkey=[task], endkey=[task, {}])
        it = iter(res)
        for row in it:
            key, value = row['key'], row['value']
            for item in value:
                yield key[1], item

    def stream(self, step, stream):
        return self.db.list(
            'glas_process/lines', 'lines',
            start_key=[step, stream],
            endkey=[step, stream, {}],
        )

    def run(self, doc):

        from .scm import ScmProc
        from .subprocess import SubProcessProc
        lookup = {
            'popen': SubProcessProc,
            'scm': ScmProc,
        }

        proc = lookup[doc.steper](self, doc)

        return proc.run()


def ProcBatch(object):

    def __init__(self, procdir):
        self.procdir = procdir

    @property
    def path(self):
        return self.procdir.path
