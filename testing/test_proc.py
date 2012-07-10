import pytest
from juggler import model, warden

def setup_module(mod):
    pytest.skip('later')

def test_start_stop_master(couchdb):

    master = Master(couchdb, 'test-master')
    master.start()
    assert master.status == 'started'
    master.stop()
