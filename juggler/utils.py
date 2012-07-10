def watch_for(db, type, status):
    #XXX: hack for tests
    for row in db.all_docs(include_docs=True):
        doc = row['doc']
        if doc['_id'][0] == '_':
            continue
        print row['doc']
        if doc.get('status') == status:
            return type.wrap(doc), None  # XXX: conflicts
    else:
        raise ValueError
