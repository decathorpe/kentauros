"""
kentauros.config.cli file
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
    function that returns a KtrConf object containing CLI settings
    """
    # if no settings were set at command line, return None
    if (CLI_ARGS.basedir is None) and \
       (CLI_ARGS.confdir is None) and \
       (CLI_ARGS.datadir is None) and \
       (CLI_ARGS.packdir is None) and \
       (CLI_ARGS.specdir is None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if CLI_ARGS.basedir is not None:
        result = KtrConf(KtrConfType.CLI,
                         basedir=os.path.abspath(CLI_ARGS.basedir))

        if CLI_ARGS.confdir is not None:
            result.confdir = CLI_ARGS.confdir
        if CLI_ARGS.datadir is not None:
            result.datadir = CLI_ARGS.datadir
        if CLI_ARGS.packdir is not None:
            result.packdir = CLI_ARGS.packdir
        if CLI_ARGS.specdir is not None:
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
        log(LOGPREFIX1 + \
            "Not all neccessary values have been set at CLI.")
        return None

