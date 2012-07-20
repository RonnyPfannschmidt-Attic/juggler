from ..model import utils, Step


def default_lookup():
    from .scm import ScmProc
    from .subprocess import SubProcessProc
    return {
        'popen': SubProcessProc,
        'scm': ScmProc,
    }


class ProcDir(object):
    scminfo = None

    def __init__(self, db, path, task):
        self.db = db
        self.path = path
        self.task = task
        self.lookup = default_lookup()

    def save_with_batch(self, doc):
        return self.db.save_doc(doc)

    def find_steps(self):
        return self.db.view('juggler/steps_of',
                            key=self.task._id,
                            include_docs=True,
                            schema=Step).all()

    def find_streams(self, task):
        res = self.db.view('juggler/streams', group='true',
                           **utils.keylist_prefix(task)).all()
        for row in res:
            key, value = row['key'], row['value']
            for item in value:
                yield key[1], item

    def stream(self, step, stream):
        return self.db.list(
            'juggler/lines', 'lines',
            start_key=[step, stream],
            endkey=[step, stream, {}],
        )

    def run(self, doc):
        proc = self.lookup[doc.steper](self, doc)
        return proc.run()
