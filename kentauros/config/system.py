"""
kentauros.config.system
reads /etc/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.init import log
from kentauros.config.common import KtrConf, KtrConfType


FILE_PATH = "/etc/kentaurosrc"
ERR_MSG = "/etc/kentaurosrc does not exist or is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.SYSTEM)
except FileNotFoundError:
    log(ERR_MSG, 1)
    CONF = None

