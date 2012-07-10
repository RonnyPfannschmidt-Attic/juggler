
from couchdbkit import schema
from couchdbkit.schema import (
    DateTimeProperty, StringProperty, IntegerProperty,
    DictProperty, BooleanProperty,
)
from reprtools import FormatRepr
from datetime import datetime


class Document(schema.StaticDocument):
    _doc_type_attr = 'type'
    type = StringProperty()


actor_transitions = [
    'new started',
    'started stopped',
    'stopped started',
    'stopped disabled',
    'disabled new',
]


class Actor(Document):
    doc_type = 'juggler:actor'

    name = StringProperty()
    belongs_to = StringProperty()
    # one of new, stopped, started, disabled
    #: one of one of cron, shedule, inbox or make
    intent = StringProperty()


class Project(Document):
    doc_type = 'juggler:project'

    computed_steps = BooleanProperty()


order_transitions = [
    'receiving received',
    'received invalid',
    'received valid',
    'valid ready',


    #XXX
]


class Order(Document):
    doc_type = 'juggler:order'

    status = StringProperty(default='receiving')
    axis = DictProperty()


class Task(Document):
    doc_type = 'juggler:task'
    __repr__ = FormatRepr('<Task {index} of {owner} - {status}>')
    status = StringProperty(default="new")
    project = StringProperty()
    arbiter = StringProperty()
    owner = StringProperty()
    order = StringProperty()
    index = IntegerProperty()
    spec = DictProperty()


class Step(Document):
    doc_type = 'juggler:step'

    __repr__ = FormatRepr('<Step {_id} of {task} started {started:%Y-%m-%d}>')

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
