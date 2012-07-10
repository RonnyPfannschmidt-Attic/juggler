import pytest


def setup_module(mod):
    pytest.skip('later')


def test_start_stop_master(couchdb):
    import Master
    master = Master(couchdb, 'test-master')
    master.start()
    assert master.status == 'started'
    master.stop()
