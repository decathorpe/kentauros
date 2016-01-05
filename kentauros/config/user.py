"""
kentauros.config.user
reads $HOME/.config/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os

from kentauros.config.common import KtrConf, KtrConfType
from kentauros.init import err
from kentauros.init.env import HOME


FILE_PATH = "~/.config/kentaurosrc"
ERR_MSG = os.path.join(HOME, ".config/kentaurosrc") + " does not exist or is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.USER)
except FileNotFoundError:
    err(ERR_MSG)
    CONF = None

