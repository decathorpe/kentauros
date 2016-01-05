"""
kentauros.config.cli
processes given command line switches to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.config.common import KtrConf, KtrConfType
from kentauros.init.cli import CLI_CONFDIR, CLI_DATADIR, CLI_SPECDIR


CONF = KtrConf()

CONF.confdir = CLI_CONFDIR
CONF.datadir = CLI_DATADIR
CONF.specdir = CLI_SPECDIR
CONF.type = KtrConfType.CLI

