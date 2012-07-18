import argparse
import yaml



parser = argparse.ArgumentParser()
parser.add_argument('database')
parser.add_argument('input')
parser.add_argument('--newid', nargs=1)


args = parser.parse_args()

from juggler.handlers.utils import get_database

db = get_database(args.database)
with open(args.input) as fp:
    data = yaml.load(fp)
if args.newid:
    data['_id'] = parser.newid

db.save_doc(data)
