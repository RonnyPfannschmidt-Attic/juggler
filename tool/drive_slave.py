import sys

from juggler import model
from juggler.handlers.utils import get_database
from juggler.handlers import shedule
from juggler import service


db = get_database(sys.argv[1])
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
