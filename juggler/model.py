
from datetime import datetime
from reprtools import FormatRepr
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
    __repr__ = FormatRepr('<Project {_id!r}>')

    description = StringProperty()
    axis = DictProperty()


class Build(Document):
    __repr__ = FormatRepr('<Build {project!r} at {added:%Y/%m/%d %H:%M}>')

    project = StringProperty()
    reason = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    axis = DictProperty()
    result = StringProperty()

    #: the current execution status of the build
    #  the order is: prepare->building->complete

    status = StringProperty(default='prepare')


class Job(Document):

    __repr__ = FormatRepr('<Job {project!r} at {added:%Y/%m/%d %H:%M} {spec}>')

    project = StringProperty()
    build = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    spec = DictProperty()


