#!/usr/bin/python
"""
juggler master

usage:
    slave.py DATABASE [WORKERS]

options:
    DATABASE     database name or uri
    WORKERS      number of workers [atm ignored]
    -h,--help    this help
"""

import docopt
args = docopt.docopt(__doc__)

from juggler.utils import get_database
from juggler.service import Juggler
from juggler.simple_slave import run_once

db = get_database(args["DATABASE"])
service = Juggler(db, db.dbname)

while True:
    run_once(service)
