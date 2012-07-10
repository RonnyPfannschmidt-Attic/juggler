import pytest


def setup_module(mod):
    pytest.skip('disabled')


def test_web(ghost):
    res, items = ghost.open('/')
    assert res.http_status == 200
#    assert 'Status' in ghost.content
