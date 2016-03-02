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

from kentauros.init import log
from kentauros.init.cli import CLI_ARGS


LOGPREFIX1 = "ktr/config/cli: "


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
        result = KtrConf(KtrConfType.CLI,
                         basedir=os.path.abspath(CLI_ARGS.basedir))

        if CLI_ARGS.confdir != None:
            result.confdir = CLI_ARGS.confdir
        if CLI_ARGS.datadir != None:
            result.datadir = CLI_ARGS.datadir
        if CLI_ARGS.packdir != None:
            result.packdir = CLI_ARGS.packdir
        if CLI_ARGS.specdir != None:
            result.specdir = CLI_ARGS.specdir

    # basedir not set: all other dirs must be specified
    else:
        result = KtrConf(KtrConfType.CLI)
        result.confdir = CLI_ARGS.confdir
        result.datadir = CLI_ARGS.datadir
        result.packdir = CLI_ARGS.packdir
        result.specdir = CLI_ARGS.specdir

    if result.validate():
        return result
    else:
        log(LOGPREFIX1 + "Not all neccessary config values have been set at CLI.")
        return None

