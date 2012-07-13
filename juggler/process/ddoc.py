import coffeescript

views = {
    'streams': {
        'map': """(doc) ->
                if doc.doc_type == "juggler:Task"
                    emit [doc._id], null;
                if doc.stream
                    emit [doc.task, doc.step], doc.stream
                return
        """,
        'reduce': """(key, values, rereduce) ->
                if rereduce
                    items = values.reduce Array.concat
                else
                    items = values
                unique = {};
                for entry in items
                    if entry != null
                        unique[entry] = true;

                key for key in unique
        """
    },
    'lines': {
        'map': '''(doc) ->
        if doc.stream && doc.line
            emit [doc.step, doc.stream, doc.lineno], doc.line
        return
        '''
    }
}


lists = {
    "lines": """(head, req) ->
          start headers: { "Content-Type": "text/plain"}
          while row = getRow()
            send row.value
          return
"""
}

rewrites = [
    {
        'from': '/lines/:step/:stream',
        'to': '_list/lines/lines/',
        'query': {
            'startkey': [':step', ':stream'],
            'endkey': [':step', ':stream', {}],
        },
    },
]

def showone(name, *path):
    print name, path
    origin = globals()[name]
    design = ddoc[name]
    for item in path:
        origin = origin[item]
        design = design[item]
    print origin
    print '-----'
    print design


def makeviews(data, path = ()):
    if isinstance(data, str):
        try:
            return coffeescript.compile(data, bare=True)
        except Exception, e:
            e.args =  (path,) + e.args
            raise
    else:
        return dict((k, makeviews(v, path + (k,))) for k, v in data.items())

ddoc = {
    '_id': '_design/glas_process',
    'views': makeviews(views),
    'lists': makeviews(lists),
    'rewrites': rewrites,
}

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('path', nargs='...')
    opts = parser.parse_args()
    showone(opts.name, *opts.path)
