"""
kentauros.config.user
reads $HOME/.config/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os

from kentauros.config.common import KtrConf, KtrConfType
from kentauros.init import log
from kentauros.init.env import HOME


FILE_PATH = os.path.join(HOME, ".config/kentaurosrc")
ERR_MSG = FILE_PATH + " does not exist or is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.USER)
except FileNotFoundError:
    log(ERR_MSG, 1)
    CONF = None

