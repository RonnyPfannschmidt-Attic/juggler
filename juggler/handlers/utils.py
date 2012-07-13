import copy
import json
from itertools import product
from functools import wraps
import couchdbkit

import logbook
log = logbook.Logger('utils')


def listen_new_changes(db, **kw):
    r = db.res.get(
        path="_changes",
        include_docs=True,
        filter='juggler/management',
        feed='continuous',
        **kw)

    r.should_close = True
    with r.body_stream() as stream:
        for line in stream:
            yield json.loads(line)


def get_database(name_or_uri):
    if '/' in name_or_uri:
        return couchdbkit.Database(name_or_uri, backend='gevent')
    else:
        return couchdbkit.Server(backend='gevent')[name_or_uri]


def _compare(obj, kw):
    log.debug('compare for \n {0}\n {1}', _cleaned(obj), kw)
    for k, v in kw.items():
        if obj.get(k) != v:
            return False
    else:
        return True


def _cleaned(doc):
    return dict((k, v) for k, v in doc.items() if v)


def watch_for(db, type, **kw):
    changes = listen_new_changes(db, type=type._doc_type)
    for row in changes:
        if 'last_seq' in row:
            raise ValueError
        doc = row['doc']
        if doc['_id'][0] == '_':
            continue
        log.debug('got in {0}', _cleaned(doc))
        if _compare(doc, kw):
            return type.wrap(doc), None  # XXX: conflicts
    else:
        raise ValueError


def steps_from_template(project, task):
    return copy.deepcopy(project.steps) or []


def generate_specs(axis):
    if not axis:
        yield {}
        return

    names, lists = zip(*sorted(axis.items()))
    for values in product(*lists):
        yield dict(zip(names, values))


def watches_for(type, status, **wkw):
    def decorator(func):
        @wraps(func)
        def watching_version(db, *k, **kw):
            log.debug('{0} {1}', k, kw)
            if k:
                item, = k
            else:
                watch_kw = {}
                for key, val in wkw.items():
                    watch_kw[key] = val(kw)

                item, _ = db.watch_for(type, status=status, **watch_kw)
            return func(db, item, **kw)
        watching_version.type = type
        watching_version.status = status
        watching_version.func = func
        return watching_version
    return decorator
