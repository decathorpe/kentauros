"""
kentauros.init.env file
"""

import os


ENVDEBUG = bool()
ENVVERBY = int()


if os.getenv("KTR_DEBUG") is None:
    ENVDEBUG = False
else:
    ENVDEBUG = True

if os.getenv("KTR_VERBOSITY") is None:
    ENVVERBY = 2
else:
    ENVVERBY = int(os.getenv("KTR_VERBOSITY"))


# get user running ktr
USER = os.getenv('USER')

# get user home
HOME = os.path.join("/home/", USER)

