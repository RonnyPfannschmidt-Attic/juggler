
from juggler import model, warden

def test_start_stop_master(couchdb):

    master = Master(couchdb, 'test-master')
    master.start()
    assert master.status == 'started'
    master.stop()
