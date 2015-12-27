"""
kentauros.config.defaults
provides default locations for
- configuration files
- source directories / tarballs
which are used if no configuration file is found.
"""

from kentauros.config import KtrConf


DEFAULT_CONF = KtrConf()
DEFAULT_CONF.basedir = "/tmp/ktr"
DEFAULT_CONF.confdir = "/tmp/ktr"
DEFAULT_CONF.datadir = "/tmp/ktr"

