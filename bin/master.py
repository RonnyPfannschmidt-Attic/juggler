#!/usr/bin/python
import sys
from juggler.service import Juggler
from juggler.handlers.utils import get_database
from juggler import simple_master
db = get_database(sys.argv[1])
juggler = Juggler(db, 'master')
simple_master.simple_master(juggler)
