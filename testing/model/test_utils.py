import pytest
from juggler.model import utils


def test_text_prefix():
    des = utils.text_prefix('_design/')
    assert des == {'startkey': '_design/', 'endkey': '_design0'}


def test_keylist_prefix():
    a = utils.keylist_prefix('a')
    assert a == {'startkey': ('a',), 'endkey': ('a', {})}


@pytest.mark.xfail(run=False, reason='test unimplemented')
def test_eventcomplete():
    pass
