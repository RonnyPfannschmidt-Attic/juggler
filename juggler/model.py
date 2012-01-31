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
    #push(dirname(__file__) + '/_design/builds', db)


def wrap(obj):
    if 'doc_type' not in obj:
        return obj
    return globals()[obj['doc_type']].wrap(obj)


class Project(Document):
    _repr_ = '<Project {_id!r}>'

    description = StringProperty()
    axis = DictProperty()


class Build(Document):
    _repr_ = '<Build {project!r} at {added:%Y/%m/%d %H:%M}>'

    project = StringProperty()
    reason = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    axis = DictProperty()
    result = StringProperty()

    #: the current execution status of the build
    #  the order is: prepare->building->complete

    status = StringProperty(default='prepare')


class Job(Document):

    _repr_ = '<Job {project!r} at {added:%Y/%m/%d %H:%M} {spec}>'

    project = StringProperty()
    build = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    spec = DictProperty()


