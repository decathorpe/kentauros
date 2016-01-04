"""
kentauros.config.default
reads /usr/share/kentauros/default.conf to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.config.common import KtrConf, KtrConfType
from kentauros.init import err

FILE_PATH = "/usr/share/kentauros/default.conf"
ERR_MSG = "/usr/share/kentauros/default.conf does not exist or it is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.DEFAULT_CONF)
except OSError:
    err(ERR_MSG)
    CONF = None

