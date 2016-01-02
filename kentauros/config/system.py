"""
kentauros.config.system
reads /etc/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.base import err
from kentauros.config.common import KtrConf, KtrConfType

FILE_PATH = "/etc/kentaurosrc"
ERR_MSG = "/etc/kentaurosrc does not exist or is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.SYSTEM_CONF)
except OSError:
    err(ERR_MSG)
    CONF = None

