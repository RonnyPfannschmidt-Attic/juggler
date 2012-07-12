listen_new_changes = partial(ChangeStream,
                             include_docs=True,
                             filter='juggler/management-status'


def _compare(obj, kw):
    for k, v in kw.items():
        if obj.get(k) != v:
            return False
    else:
        return True


def watch_for(db, type, **kw):
    #XXX: hack for tests
    for row in db.all_docs(include_docs=True, filter):
        doc = row['doc']
        if doc['_id'][0] == '_':
            continue
        print row['doc']
        if _compare(doc, kw):
            return type.wrap(doc), None  # XXX: conflicts
    else:
        raise ValueError
