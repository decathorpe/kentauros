"""
kentauros.init module
"""

import enum
import sys

from kentauros.init.env import ENVDEBUG, ENVVERBY
from kentauros.init.cli import CLIArgs, get_parsed_cli


__all__ = []


def __smaller_int__(int1, int2):
    if int1 < int2:
        return int1
    else:
        return int2


def get_debug():
    "calculate debug status from environment variables and CLI arguments"
    cli_args = CLIArgs()
    cli_args.parse_args(get_parsed_cli())
    return ENVDEBUG or cli_args.debug


def get_verby():
    "calculate verbosity from environment variables and CLI arguments"
    cli_args = CLIArgs()
    cli_args.parse_args(get_parsed_cli())
    return __smaller_int__(ENVVERBY, cli_args.verby)


def dbg(msg):
    """
    kentauros.init.dbg()
    prints debug messages if DEBUG is True
    set by --debug or by environment variable KTR_DEBUG=1
    """
    if get_debug():
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
    if (pri >= get_verby()) or get_debug():
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

