from .structure import Event


def complete_event(doc, index, step, task):
    if isinstance(doc, dict):
        doc = Event(**doc)
    if not doc._id:
        doc._id = '%s:%s' % (step._id, index)
    if not doc.step:
        doc.step = step._id
    if not doc.task:
        doc.task = task._id
    doc.index = index
    return doc


def text_prefix(text):
    #XXX: implement max unicode
    lastchar = text[-1]
    #XXX: unicode?
    lastchar = chr(ord(lastchar) + 1)
    return {'startkey': text, 'endkey': text[:-1] + lastchar}


def keylist_prefix(*k):
    return {'startkey': k, 'endkey': k + ({},)}
