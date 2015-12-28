"""
kentauros.config.cli
processes given command line switches to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.config.common import KtrConf, KtrConfType

CONF = KtrConf()
CONF.type = KtrConfType.CLI_CONF

