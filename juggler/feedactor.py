import gevent
from couchdb import ChangeFeed

from .model import Actor

from abc import ABCMeta, abstractmethod

class FeedActor(object):
    __metaclass__ = ABCMeta
    def __init__(self, db, actor_docid):
        self.db = db
        self.actor_docif = actor_docid

    def start(self):
        assert self.actor_doc.status in ('new', 'stopped')
        self.actor_doc.status = 'started'
        self.db.save_doc(self.actor_doc)
        self._listener = gevent.spawn(self._listen_changes)
        #XXX: add a link for shutdown handling

    def stop(self):
        self._listener.kill()
        self.actor_doc.status = 'stopped'
        self.db.save_doc(self.actor_doc)

    def _listen_changes(self):
        pass

    @abstractmethod
    def handle_change(self, docid, revs):
        pass

