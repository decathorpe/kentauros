"""
This subpackage contains the :py:class:`Kentauros` class, which holds
configuration values parsed from CLI arguments, environment variables and
configuration files. The implementation makes sure that command line arguments,
environment variables and configuration files are parsed only once per program
run. Additionally, this subpackage holds logging and error printing functions.
"""


import sys

from kentauros.definitions import InstanceType

from kentauros.config import ktr_get_conf
from kentauros.init.cli import CLI_ARGS_DICT
from kentauros.init.env import get_env_debug, get_env_verby


def __smaller_int__(int1, int2):
    if int1 < int2:
        return int1
    else:
        return int2


class Kentauros:
    """
    # TODO: napoleon class docstring
    instance class with dict class variable, as a "Borg", a quasi-singleton
    """

    # pylint: disable=too-few-public-methods
    saved_state = dict()

    def __getattr__(self, attr):
        return self.saved_state.__getitem__(attr)

    def __setattr__(self, attr, val):
        self.saved_state.__setitem__(attr, val)

    def __init__(self, itype=InstanceType.NORMAL):
        assert isinstance(itype, InstanceType)

        self.itype = itype

        if "cli" not in self.saved_state:
            self.cli = CLI_ARGS_DICT[itype](itype)

        if "debug" not in self.saved_state:
            self.debug = get_env_debug() or self.cli.get_debug()

        if "verby" not in self.saved_state:
            self.verby = __smaller_int__(get_env_verby(), self.cli.get_verby())

        if "conf" not in self.saved_state:
            self.conf = ktr_get_conf(itype)


def dbg(msg):
    """
    # TODO: napoleon function docstring
    kentauros.init.dbg()
    prints debug messages if DEBUG is True
    set by --debug or by environment variable KTR_DEBUG=1
    """
    if Kentauros().debug:
        print("DEBUG: " + str(msg))


def err(msg):
    """
    # TODO: napoleon function docstring
    kentauros.init.err()
    prints error messages to sys.stderr
    format: ERROR: <message>
    """

    print("ERROR: " + msg, file=sys.stderr)


def log(msg, pri=2):
    """
    # TODO: napoleon function docstring
    kentauros.init.log():
    prints log messages if "priority" is equal or less to verbosity level.
    priority levels mean (2 is the default):
    - 0: every message is printed and subprocesses are invoked with --verbose
    - 1: some messages are printed and subprocesses get no CLI flags
    - 2: few messages are printed and subprocesses are invoked with --quiet
    format: <message>
    """
    if (pri >= Kentauros().verby) or Kentauros().debug:
        print(msg)


def log_command(prefix1, basename, cmdlist, pri=2):
    """
    # TODO: napoleon function docstring
    kentauros.init.log_command():
    prints commands that are executed using the subprocess module.
    """
    cmdstr = ""
    prefix2 = " " * len(prefix1)

    for cmd in cmdlist:
        cmdstr += (cmd + " ")

    log(prefix1 + basename + " command:", pri)
    log(prefix2 + cmdstr, pri)

