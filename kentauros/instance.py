"""
contains KtrInstance class that holds CLI and other status things
"""

import sys

from kentauros.definitions import InstanceType

from kentauros.config import ktr_get_conf
from kentauros.init.cli import CLIArgs
from kentauros.init.env import ENVDEBUG, ENVVERBY


def __smaller_int__(int1, int2):
    if int1 < int2:
        return int1
    else:
        return int2


class Kentauros:
    """
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

        if "cli" not in self.saved_state:
            self.cli = CLIArgs(itype)

        if "debug" not in self.saved_state:
            self.debug = ENVDEBUG or self.cli.debug

        if "verby" not in self.saved_state:
            self.verby = __smaller_int__(ENVVERBY, self.cli.verby)

        if "conf" not in self.saved_state:
            self.conf = ktr_get_conf()


def dbg(msg):
    """
    kentauros.init.dbg()
    prints debug messages if DEBUG is True
    set by --debug or by environment variable KTR_DEBUG=1
    """
    if Kentauros().debug:
        print("DEBUG: " + str(msg))


def err(msg):
    """
    kentauros.init.err()
    prints error messages to sys.stderr
    format: ERROR: <message>
    """

    print("ERROR: " + msg, file=sys.stderr)


def log(msg, pri=2):
    """
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
    kentauros.init.log_command():
    prints commands that are executed using the subprocess module.
    """
    cmdstr = ""
    prefix2 = " " * len(prefix1)

    for cmd in cmdlist:
        cmdstr += (cmd + " ")

    log(prefix1 + basename + " command:", pri)
    log(prefix2 + cmdstr, pri)

