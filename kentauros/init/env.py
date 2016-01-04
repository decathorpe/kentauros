"""
kentauros.init.env
"""

import os


ENVDEBUG = bool()
ENVVERBY = int()


if os.getenv("KTR_DEBUG") == None:
    ENVDEBUG = False
else:
    ENVDEBUG = True

if os.getenv("KTR_VERBOSITY") == None:
    ENVVERBY = 2
else:
    ENVVERBY = int(os.getenv("KTR_VERBOSITY"))


# check if being run as root (EUID == 0)
ROOT = not bool(os.geteuid())

# get user running ktr
USER = os.getenv('USER')

# get user home
HOME = os.path.join("/home/", USER)

