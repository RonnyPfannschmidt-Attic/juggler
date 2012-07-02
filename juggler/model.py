
from couchdbkit import schema
from couchdbkit.schema import (
    DateTimeProperty, StringProperty, IntegerProperty,
    DictProperty,
)
from reprtools import FormatRepr
from datetime import datetime

class Document(schema.Document):
    _doc_type_attr = 'type'
    type = StringProperty()

class Actor(Document):
    doc_type = 'juggler:actor'
    transitions = [
        'new started',
        'started stopped',
        'stopped started',
        'stopped disabled',
        'disabled new',
    ]



    name = StringProperty()

    # one of new, stopped, started, disabled
    state = StringProperty(default='new')
    current_host = StringProperty()
    current_pid = IntegerProperty()
    last_use = DateTimeProperty()

    #: one of one of cron, shedule, inbox or make
    intent = StringProperty()



class Project(Document):
    doc_type = 'juggler:project'



class Order(Document):
    doc_type = 'juggler:order'
    transitions = [

        'receiving received',
        'received invalid',
        'received valid',
        #XXX
    ]
        

    state = StringProperty(default='receiving')


class Task(Document):
    doc_type = 'juggler:task'
    __rerp__ = FormatRepr('<Task {belongs_to} {status}>')

class Step(Document):
    doc_type = 'juggler:step'

    __repr__ = FormatRepr('<Step of {task} started {started:%Y-%m-%d}>')

    task = StringProperty(required=True)
    status = StringProperty(default='prepared')
    steper = StringProperty()
    started = DateTimeProperty(default=datetime.utcnow)
    finished = DateTimeProperty(default=None)

class Event(Document):
    doc_type = 'juggler:event'
    __repr__ = FormatRepr(r'<Event {step} {index}>')

    step = StringProperty()
    index = IntegerProperty()

