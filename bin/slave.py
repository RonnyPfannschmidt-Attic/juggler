#!/usr/bin/python
import argparse

from juggler.handlers.utils import get_database
from juggler.service import Juggler
from juggler.simple_slave import simple

parser = argparse.ArgumentParser()
parser.add_argument('database')
parser.add_argument('name')
sp = parser.add_subparsers()

simple_parser = sp.add_parser('simple')
simple_parser.set_defaults(func=simple)

args = parser.parse_args()


db = get_database(args.database)
service = Juggler(db, args.name)

args.func(service, args)
