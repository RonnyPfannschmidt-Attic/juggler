import sys

from juggler import model
from juggler.utils import get_database
from juggler import workers
from juggler import service


db = get_database(sys.argv[1])
j = service.Juggler(db, None)

project = model.Project(steps=[])
j.save_doc(project)

task = model.Task(
    project=project._id,
    spec=None,
    status='pending')
j.save_doc(task)


workers.approve_claimed_task(j)
