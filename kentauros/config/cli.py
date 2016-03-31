"""
This module contains :py:func:`get_cli_config` function, which parses a
:py:class:`CLIArgs` instance for settings defined by CLI arguments. Those
settings include - at the moment - the base directory for kentauros data
(`--basedir`), the directory for package configuration files (`--confdir`), the
directory for package sources (`--datadir`), the directory for buildable source
packages (`--packdir`) and the package specification directory (`--specdir`).
"""


import os

from kentauros.definitions import KtrConfType, InstanceType

from kentauros.config.common import KtrConf
from kentauros.init.cli import CLI_ARGS_DICT


LOGPREFIX1 = "ktr/config/cli: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def get_cli_config(itype: InstanceType) -> KtrConf:
    """
    This function reads and parses command line settings and switches and puts
    them into a :py:class:`KtrConf` instance for further processing.

    Returns:
        KtrConf: settings parsed from command line settings or switches
    """

    assert isinstance(itype, InstanceType)

    cli_args = CLI_ARGS_DICT[itype]()

    # if no settings were set at command line, return None
    if (cli_args.get_ktr_basedir() is None) and \
       (cli_args.get_ktr_confdir() is None) and \
       (cli_args.get_ktr_datadir() is None) and \
       (cli_args.get_ktr_packdir() is None) and \
       (cli_args.get_ktr_specdir() is None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if cli_args.basedir is not None:
        result = KtrConf(KtrConfType.CLI,
                         basedir=os.path.abspath(cli_args.basedir))

        if cli_args.confdir is not None:
            result.confdir = os.path.abspath(cli_args.confdir)
        if cli_args.datadir is not None:
            result.datadir = os.path.abspath(cli_args.datadir)
        if cli_args.packdir is not None:
            result.packdir = os.path.abspath(cli_args.packdir)
        if cli_args.specdir is not None:
            result.specdir = os.path.abspath(cli_args.specdir)

    # basedir not set: all other dirs must be specified
    else:
        result = KtrConf(KtrConfType.CLI)
        result.confdir = os.path.abspath(cli_args.confdir)
        result.datadir = os.path.abspath(cli_args.datadir)
        result.packdir = os.path.abspath(cli_args.packdir)
        result.specdir = os.path.abspath(cli_args.specdir)

    if result.validate():
        return result
    else:
        print(LOGPREFIX1 + \
            "Not all neccessary values have been set at CLI.")
        return None

