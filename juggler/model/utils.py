def make_id(memo, prefix, name, given=None):
    """
    utility to create ids,
    """
    if given is not None:
        return given
    current = memo.get(name, 0)
    memo[name] = current + 1
    suffix = '_%s' % current if current else ""
    return '%s:%s%s' % (prefix, name, suffix)


def text_prefix(text):
    #XXX: implement max unicode
    lastchar = text[-1]
    #XXX: unicode?
    lastchar = chr(ord(lastchar) + 1)
    return {'startkey': text, 'endkey': text[:-1] + lastchar}


def keylist_prefix(*k):
    return {'startkey': k, 'endkey': k + ({},)}
