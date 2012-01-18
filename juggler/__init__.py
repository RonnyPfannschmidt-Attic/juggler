

# do all the monkeypatching
import gevent.monkey
gevent.monkey.patch_all()

from restkit.globals import set_manager
from restkit.manager.mgevent import GeventManager

# set the gevent connection manager
set_manager(GeventManager())

