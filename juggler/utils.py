from functools import partial
from couchdbkit.changes import ChangesStream


listen_new_changes = partial(
    ChangesStream,
    include_docs=True,
    filter='juggler/management',
)


def _compare(obj, kw):
    for k, v in kw.items():
        if obj.get(k) != v:
            return False
    else:
        return True


def watch_for(db, type, **kw):
    #XXX: hack for tests
    changes = listen_new_changes(db, type=type._doc_type)
    for row in changes:
        doc = row['doc']
        if doc['_id'][0] == '_':
            continue
        print row['doc']
        if _compare(doc, kw):
            return type.wrap(doc), None  # XXX: conflicts
    else:
        raise ValueError
