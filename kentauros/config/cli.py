"""
kentauros.config.cli
processes given command line switches to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
- directory containing spec files (specdir)
"""

import os

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType
from kentauros.init.cli import CLI_ARGS


def get_cli_config():
    """
    kentauros.config.cli.get_cli_config():
    function that returns a KtrConf object containing CLI_????DIR settings
    """
    # if no settings were set at command line, return None
    if (CLI_ARGS.basedir == None) and \
       (CLI_ARGS.confdir == None) and \
       (CLI_ARGS.datadir == None) and \
       (CLI_ARGS.packdir == None) and \
       (CLI_ARGS.specdir == None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if CLI_ARGS.basedir != None:
        result = KtrConf()
        result['main'] = {}
        result['main']['basedir'] = os.path.abspath(CLI_ARGS.basedir)

        if CLI_ARGS.confdir == None:
            result['main']['confdir'] = os.path.join(result['main']['basedir'], "configs")
        else:
            result['main']['confdir'] = CLI_ARGS.confdir

        if CLI_ARGS.datadir == None:
            result['main']['datadir'] = os.path.join(result['main']['basedir'], "sources")
        else:
            result['main']['datadir'] = CLI_ARGS.datadir

        if CLI_ARGS.packdir == None:
            result['main']['packdir'] = os.path.join(result['main']['basedir'], "packages")
        else:
            result['main']['packdir'] = CLI_ARGS.packdir

        if CLI_ARGS.specdir == None:
            result['main']['specdir'] = os.path.join(result['main']['basedir'], "specs")
        else:
            result['main']['specdir'] = CLI_ARGS.specdir

        result.type = KtrConfType.CLI
        return result

    # default case: mix-and-match of set and not set config values
    else:
        result = KtrConf()
        result['main'] = {}
        result['main']['basedir'] = CLI_ARGS.basedir
        result['main']['confdir'] = CLI_ARGS.confdir
        result['main']['datadir'] = CLI_ARGS.datadir
        result['main']['packdir'] = CLI_ARGS.packdir
        result['main']['specdir'] = CLI_ARGS.specdir
        result.type = KtrConfType.CLI
        return result

