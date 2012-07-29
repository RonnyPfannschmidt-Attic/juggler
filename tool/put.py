import argparse
import yaml
from juggler.handlers.utils import get_database


parser = argparse.ArgumentParser()
parser.add_argument('database')
parser.add_argument('input')
parser.add_argument('--newid')

args = parser.parse_args()


def main(db, args):
    with open(args.input) as fp:
        data = yaml.load(fp)

    if args.newid:
        data['_id'] = args.newid

    db.save_doc(data)


if __name__ == '__main__':
    db = get_database(args.database)
    main(db, args)
