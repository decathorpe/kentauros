"""
kentauros.config.cli
processes given command line switches to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
- directory containing spec files (specdir)
"""

from kentauros.config.common import KtrConf, KtrConfType

from kentauros.init.cli import CLI_BASEDIR, CLI_CONFDIR
from kentauros.init.cli import CLI_DATADIR, CLI_SPECDIR


def get_cli_config():
    """
    kentauros.config.cli.get_cli_config():
    function that returns a KtrConf object containing CLI_????DIR settings
    """
    if (CLI_BASEDIR == None) and \
       (CLI_CONFDIR == None) and \
       (CLI_DATADIR == None) and \
       (CLI_SPECDIR == None):
        return None
    else:
        result = KtrConf()
        result['main'] = {}
        result['main']['basedir'] = CLI_BASEDIR
        result['main']['confdif'] = CLI_CONFDIR
        result['main']['datadir'] = CLI_DATADIR
        result['main']['specdir'] = CLI_SPECDIR
        result.type = KtrConfType.CLI
        return result

