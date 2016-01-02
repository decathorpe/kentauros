"""
kentauros.config.user
reads $HOME/.config/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.base import err
from kentauros.config.common import KtrConf, KtrConfType

FILE_PATH = "~/.config/kentaurosrc"
ERR_MSG = "$HOME/.config/kentaurosrc does not exist or is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.USER_CONF)
except OSError:
    err(ERR_MSG)
    CONF = None

