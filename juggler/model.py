
from couchdbkit.schema import Document #, DocumentSchemaProperty
from couchdbkit.schema import (
    DateTimeProperty, StringProperty, IntegerProperty,
    DictProperty,
)
from reprtools import FormatRepr
from datetime import datetime

class Driver(Document):
    doc_type = 'juggler:driver'

    current_host = StringProperty()
    current_pid = IntegerProperty()
    last_use = DateTimeProperty()

    #: one of one of cron, shedule, inbox or make
    intent = StringProperty()



class Project(Document):
    doc_type = 'juggler:project'


class Task(Document):
    doc_type = 'juggler:task'
    __rerp__ = FormatRepr('<Task {belongs_to} {status}>')

class Step(Document):
    doc_type = 'juggler:step'

    __repr__ = FormatRepr('<Step of {task} started {started:%Y-%m-%d}>')

    task = StringProperty(required=True)
    status = StringProperty(default='prepared')
    inputs = DictProperty()
    steper = StringProperty()
    started = DateTimeProperty(default=datetime.utcnow)
    finished = DateTimeProperty(default=None)

class Event(Document):
    doc_type = 'juggler:event'
    __repr__ = FormatRepr(r'<Event {step} {index}>')

    step = StringProperty()
    index = IntegerProperty()

