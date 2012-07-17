import pytest
from juggler.handlers.utils import translate_variables

specs = [
    # id, items, spec, result
    ('nothing', {}, {}, {}),
    ('some', {}, {'a': 1}, {}),
    ('flat', {'__var__': 'a'}, {'a': 1}, 1),
]


@pytest.mark.parametrize(
    ('items', 'spec', 'result'),
    [x[1:] for x in specs],
    ids=[x[0] for x in specs])
def test_translate_variables(items, spec, result):
    translated = translate_variables(items, spec)
    assert translated == result
