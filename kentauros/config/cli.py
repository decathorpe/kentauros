"""
kentauros.config.cli
processes given command line switches to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
- directory containing spec files (specdir)
"""

from kentauros.config.common import KtrConf, KtrConfType
from kentauros.init.cli import CLI_CONFDIR, CLI_DATADIR, CLI_SPECDIR


CONF = KtrConf()

if (CLI_CONFDIR == None) and (CLI_DATADIR == None) and (CLI_SPECDIR == None):
    CONF = None
else:
    CONF.confdir = CLI_CONFDIR
    CONF.datadir = CLI_DATADIR
    CONF.specdir = CLI_SPECDIR
    CONF.type = KtrConfType.CLI

