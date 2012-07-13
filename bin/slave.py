#!/usr/bin/python
import argparse

from juggler.handlers.utils import get_database
from juggler.service import Juggler
from juggler.simple_slave import claim, work, simple

parser = argparse.ArgumentParser()
parser.add_argument('database')
parser.add_argument('name')
sp = parser.add_subparsers()
claim_parser = sp.add_parser('claim')
claim.set_defaults(func=claim)
#XXX: configure in database
claim.add_argument('--set-backlog', type=int, default=None)


work_parser = sp.add_parser('work')
work.set_defaults(func=work)
work.add_argument('id')

simple_parser = sp.add_parser('simple')
simple_parser.set_defaults(func=simple)

args = parser.parse_args()


db = get_database(args.database)
service = Juggler(db, args.name)

args.func(service, args)
