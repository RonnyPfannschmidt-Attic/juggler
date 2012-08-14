from __future__ import print_function
from operator import itemgetter
from juggler.handlers.utils import get_database

#XXX: one place for states
#XXX: think about extra state data like owner

messy_states = u'building', u'claimed', u'claiming'


def clean_data_of_task(db, taskid):
    print('cleaning data of', taskid)
    
    items = db.all_docs(
        startkey=taskid + ':',
        endkey=taskid + ';',
        wrapper=lambda row: dict(
            _id=row[u'id'],
            _rev=row[u'value'][u'rev'],
        ),
    ).all()
    print('killing', len(items), 'items')
    db.bulk_delete(items)
    pass

def main(db):
    info = db.view('juggler/stm',
                   startkey=['juggler:task'],
                   endkey=['juggler:task', {}],
                   group=True).all()
    items = dict(
        (x[u'key'][1], x[u'value'])
        for x in info
        if x[u'key'][1] in messy_states
    )

    for state in items:
        print('reseting', items[state], 'of', state, 'to new')
        listing = db.view('juggler/stm',
                        key=[u'juggler:task', state],
                        reduce=False,
                        wrapper=itemgetter(u'id')
                       ).all()
        for item in listing:
            clean_data_of_task(db, item)
            data = db.get(item)
            data[u'status'] = 'new'
            data[u'owner'] = None
            db.save_doc(data)


if __name__ == '__main__':
    import sys
    db = get_database(sys.argv[1])
    main(db)

