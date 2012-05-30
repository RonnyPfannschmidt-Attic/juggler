
from couchdbkit.schema import Document #, DocumentSchemaProperty
from couchdbkit.schema import DateTimeProperty, StringProperty
from reprtools import FormatRepr
from datetime import datetime

class Driver(Document):
    doc_type = 'juggler:driver'

    current_host = str
    current_pid = int
    last_use = datetime

    #: one of one of cron, shedule, inbox or make
    intent = str



class Project(Document):
    doc_type = 'juggler:project'


class Task(Document):
    #XXX: dummy
    __rerp__ = FormatRepr('<Task {belongs_to} {status}>')

class Step(Document):
    doc_type = 'juggler:step'

    __repr__ = FormatRepr('<Step of {task} started {started:%Y-%m-%d}>')

    task = str
    status = StringProperty(default='prepared')
    inputs = dict
    steper = str
    started = DateTimeProperty(default=datetime.utcnow)
    finished = DateTimeProperty(default=None)

class Event(Document):
    doc_type = 'juggler:event'
    __repr__ = FormatRepr(r'<Event {step} {index}>')

    step = str
    index = int






