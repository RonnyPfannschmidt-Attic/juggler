
from couchdbkit.schema import Document
from reprtools import FormatRepr


class Driver(Document):
    doc_type = 'juggler:driver'

    current_host = str
    current_pid = int
