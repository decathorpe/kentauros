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
from kentauros.init.cli import CLIArgs, get_parsed_cli


LOGPREFIX1 = "ktr/config/cli: "


def get_cli_config():
    """
    kentauros.config.cli.get_cli_config():
    function that returns a KtrConf object containing CLI settings
    """

    cli_args = CLIArgs()
    cli_args.parse_args(get_parsed_cli())

    # if no settings were set at command line, return None
    if (cli_args.basedir is None) and \
       (cli_args.confdir is None) and \
       (cli_args.datadir is None) and \
       (cli_args.packdir is None) and \
       (cli_args.specdir is None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if cli_args.basedir is not None:
        result = KtrConf(KtrConfType.CLI,
                         basedir=os.path.abspath(cli_args.basedir))

        if cli_args.confdir is not None:
            result.confdir = cli_args.confdir
        if cli_args.datadir is not None:
            result.datadir = cli_args.datadir
        if cli_args.packdir is not None:
            result.packdir = cli_args.packdir
        if cli_args.specdir is not None:
            result.specdir = cli_args.specdir

    # basedir not set: all other dirs must be specified
    else:
        result = KtrConf(KtrConfType.CLI)
        result.confdir = cli_args.confdir
        result.datadir = cli_args.datadir
        result.packdir = cli_args.packdir
        result.specdir = cli_args.specdir

    if result.validate():
        return result
    else:
        log(LOGPREFIX1 + \
            "Not all neccessary values have been set at CLI.")
        return None

