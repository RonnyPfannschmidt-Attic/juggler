import copy
import json
import math
from itertools import product
from functools import wraps
import couchdbkit
from juggler.async import _BACKEND, _magic_stop

import logbook
log = logbook.Logger('utils', level='info')

#: provate variable for test settings injection
_CHANGES_EXTRA = {}


def listen_some_changes(db, **kw):
    db = get_database(db.uri)
    r = db.res.get(
        path="_changes",
        include_docs=True,
        filter='juggler/management',
        feed='longpoll',
        **dict(_CHANGES_EXTRA, **kw))

    r.should_close = True
    with r.body_stream() as stream:
        return json.load(stream)


def listen_new_changes(db, **kw):
    since = kw.pop('since', 0)
    while True:
        _magic_stop()
        result = listen_some_changes(db, since=since, **kw)
        since = result['last_seq']
        for item in result['results']:
            _magic_stop()
            yield item


def get_database(name_or_uri):
    if '/' in name_or_uri:
        return couchdbkit.Database(name_or_uri, backend=_BACKEND)
    else:
        return couchdbkit.Server(backend=_BACKEND)[name_or_uri]


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
        doc = row['doc']
        if doc['_id'][0] == '_':
            continue
        log.debug('got in {0}', _cleaned(doc))
        if _compare(doc, kw):
            return type.wrap(doc), None  # XXX: conflicts


def translate_variables(template, spec):
    #XXX: prelimitary
    if isinstance(template, dict):
        if template.keys() == ['__var__']:
            return spec[template['__var__']]
        else:
            result = {}
            for k, v in template.items():
                result[k] = translate_variables(v, spec)
            return result
    elif isinstance(template, list):
        return [translate_variables(i, spec) for i in template]
    else:
        return template


def steps_from_template(project, task):
    steps = copy.deepcopy(project.steps) or []
    precission = int(math.log(len(steps) * 10 + 1, 10))
    for idx, step in enumerate(steps):
        step['_id'] = "%s:step_%*d" % (task._id, precission, idx)
        step['type'] = 'juggler:step'
        step['index'] = idx
        step['task'] = task._id
        step.update(translate_variables(step, task.spec))
    return steps


def generate_specs(axis):
    if not axis:
        yield {}
        return

    names, lists = zip(*sorted(axis.items()))
    for values in product(*lists):
        yield dict(zip(names, values))


def gather_next(db, type, status, **watch_kw):
    since = 0

    params = dict(
        key=[type._doc_type, status],
        include_docs=True,
        update_seq=True,
        reduce=False)
    if not watch_kw:
        params.update(limit=1)

    results = db.db.raw_view('/_design/juggler/_view/stm', params)
    results = results.json_body
    rows = results.pop('rows')
    if rows:
        if watch_kw:
            for row in rows:
                if _compare(row['doc'], watch_kw):
                    return type.wrap(row['doc']), results
            assert 0
        else:
            return type.wrap(rows[0]['doc']), results
    since = results['last_seq']

    return db.watch_for(type, status=status, since=since, **watch_kw)


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

                item, _ = gather_next(db, type, status=status, **watch_kw)
            return func(db, item, **kw)
        watching_version.type = type
        watching_version.status = status
        watching_version.func = func
        return watching_version
    return decorator
