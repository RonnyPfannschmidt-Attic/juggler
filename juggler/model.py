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

class FancyDocument(Document):
    _repr = '<{self.__class__.__name__} at 0x{id:x}>'
    def __repr__(self):
        return self._repr.format(self=self, id=id(self)) #XXX: pain


class Project(FancyDocument):
    _repr = '<Project {self._id!r}>'

    description = StringProperty()
    axis = DictProperty()


class Build(FancyDocument):
    _repr = '<Build {self.project!r} at {self.added:%Y/%m/%d %H:%M}>'

    project = StringProperty()
    reason = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    axis = DictProperty()
    result = StringProperty()

    #: the current execution status of the build
    #  the order is: prepare->building->complete

    status = StringProperty(default='prepare')



class Job(FancyDocument):

    _repr = '<Job {self.project!r} at {self.added:%Y/%m/%d %H:%M} {self.spec}>'

    project = StringProperty()
    build = StringProperty()
    added = DateTimeProperty(default=datetime.utcnow)
    spec = DictProperty()


