"""
kentauros.config.project
reads project-specific ./kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.base import err
from kentauros.config.common import KtrConf, KtrConfType

FILE_PATH = "./kentaurosrc"
ERR_MSG = "This directory does not contain a kentaurosrc file, or it is not readable."

CONF = KtrConf()

try:
    CONF.read(filepath=FILE_PATH,
              conftype=KtrConfType.PROJECT_CONF)
except OSError:
    err(ERR_MSG)
    CONF = None

