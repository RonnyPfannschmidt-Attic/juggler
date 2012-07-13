import sys
import py
import subprocess

from juggler import model
from juggler.handlers.utils import get_database
from juggler.handlers import shedule
from juggler import service

path = py.path.local(__file__).dirpath().dirpath().join('composeapp').strpath

db = get_database(sys.argv[1])
print 'clean'
try:
    del db.server[sys.argv[1]]
except:
    pass

subprocess.check_call(
    ['couchdb-compose', 'push', sys.argv[1]],
    cwd = path,
)

j = service.Juggler(db, None)

project = model.Project(steps=[])
j.save_doc(project)

task = model.Task(
    project=project._id,
    spec=None,
    status='pending')
print 'save'
j.save_doc(task)

print 'approve'
shedule.approve_claimed_task(j)
