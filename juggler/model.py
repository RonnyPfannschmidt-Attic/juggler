from datetime import datetime
from couchdbkit import (
    Document,
    StringProperty,
    DictProperty,
    DateTimeProperty,
)

def setup_design(db):
    from couchdbkit.designer import push
    from os.path import dirname
    push(dirname(__file__) + '/_design/jobs', db)
    push(dirname(__file__) + '/_design/builds', db)


class Job(Document):
    
    project = StringProperty()
    build = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    spec = DictProperty()

    def __repr__(self):
        return '<Job {project!r} at {added:%Y/%m/%d %H:%M} {spec}>'.format(
            project=self.project,
            added=self.added,
            spec=self.spec,
        )


class Project(Document):
    description = StringProperty()
    axis = DictProperty()

    def __repr__(self):
        return '<Project %r>' % self.id

class Build(Document):
    project = StringProperty()
    reason = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    axis = DictProperty()

    def __repr__(self):
        return '<Build {project!r} at {added:%Y/%m/%d %H:%M}>'.format(
            project=self.project,
            added=self.added,
        )
