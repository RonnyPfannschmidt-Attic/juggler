from functools import partial
from juggler.model import utils


def test_idmaker():
    d = {}

    m = partial(utils.make_id, d, 'test')
    id = m('python')
    assert id == 'test:python'
    id = m('python')
    assert id == 'test:python_1'
    id = m('python', 'python')
    assert id == 'python'

    assert d == {'python': 2}


def test_text_prefix():
    des = utils.text_prefix('_design/')
    assert des == {'startkey': '_design/', 'endkey': '_design0'}


def test_keylist_prefix():
    a = utils.keylist_prefix('a')
    assert a == {'startkey': ('a',), 'endkey': ('a', {})}
