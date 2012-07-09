import gevent
from couchdb import ChangeFeed

from .model import Actor

from abc import ABCMeta, abstractmethod
from logbook import Logger

log = Logger('feed actor')


class FeedActor(object):
    __metaclass__ = ABCMeta
    actor_doc = None

    def __init__(self, db, actor_docid):
        self.stoping = False
        self.db = db
        self.actor_docid = actor_docid

    def start(self):
        self.actor_doc = doc = db.get(self.actor_docid, schema=Actor)
        assert self.actor_doc.status in ('new', 'stopped')
        doc.pop('exception')
        
        try:
            self._listener = gevent.spawn(self._listen_changes)
        except Exception as e: 
            log.exception('failed to start actor{actor_doc.id}', actor_doc=self.actor_doc)
            self.actor_doc.status = 'started'
            doc.exception = {'type': type(e).__name__, 'text': str(e)}
        else:
            self.actor_doc.status = 'started'
        finally:
            self.db.save_doc(self.actor_doc)
        #XXX: add a link for shutdown handling

    def stop_listener(self):
        self.stoping = True
        self._listener.kill()
        self.actor_doc.status = 'stopped'
        self.db.save_doc(self.actor_doc)

    

    def _listen_changes(self):
        pass
