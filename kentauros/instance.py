"""
This submodule contains the :py:class:`Kentauros` class, which holds configuration values parsed
from CLI arguments, environment variables and configuration files. The implementation makes sure
that command line arguments, environment variables and configuration files are parsed only once per
program run. Additionally, this subpackage holds logging and error printing functions.
"""


import sys

from kentauros.config import ktr_get_conf
from kentauros.init.cli import CLIArgs
from kentauros.init.env import get_env_debug, get_env_verby
from kentauros.state import KtrStater


def __smaller_int__(int1: int, int2: int):
    if int1 < int2:
        return int1
    else:
        return int2


class Kentauros:
    """
    This class stores settings and variables that must be the same during the execution of code from
    the "kentauros" package. This is accomplished by storing the critical data in a class variable,
    which is initialised only once per execution.

    It also provides methods for printing log, error and debug messages to stdout or stderr.

    Attributes:
        dict saved_state:   stores critical values during the kentauros python package execution

    Arguments:
        InstanceType itype: type of kentauros instance (normal, config, create)
    """

    saved_state = dict()

    def __getattr__(self, attr: str):
        return self.saved_state.__getitem__(attr)

    def __setattr__(self, attr: str, val):
        self.saved_state.__setitem__(attr, val)

    def __init__(self, log_prefix: str=None):
        if log_prefix is not None:
            assert isinstance(log_prefix, str)

        self.log_prefix = log_prefix

        if "cli" not in self.saved_state:
            self.cli = CLIArgs()

        if "debug" not in self.saved_state:
            self.debug = get_env_debug() or self.cli.get_debug()

        if "verby" not in self.saved_state:
            self.verby = __smaller_int__(get_env_verby(), self.cli.get_verby())

        if "conf" not in self.saved_state:
            self.conf = ktr_get_conf()

        if "state" not in self.saved_state:
            self.state = KtrStater()

    def dbg(self, msg: str, prefix: str=None):
        """
        This method prints messages with a "DEBUG: " prefix to stdout, but only if the *KTR_DEBUG*
        environment variable has been set or the `--debug` or `-d` flag has been supplied at the
        command line.

        Arguments:
            str msg: debug message to be printed
        """

        if not self.debug:
            return

        assert isinstance(msg, str)

        if prefix is not None:
            print("DEBUG: " + prefix + " " + msg)
            return

        if self.log_prefix is not None:
            print("DEBUG: " + self.log_prefix + " " + msg)
            return

        print("DEBUG: " + msg)

    def err(self, msg: str, prefix: str=None):
        """
        This method prints messages with an "ERROR: " prefix to standard error output, regardless
        of environment variables and CLI settings supplied.

        Arguments:
            str msg: error message to be printed
        """

        if prefix is None:
            if self.log_prefix is None:
                self.log(msg, prefix="ERROR: ", outfile=sys.stderr)
            else:
                self.log(msg, prefix="ERROR: " + self.log_prefix, outfile=sys.stderr)
        else:
            self.log(msg, prefix="ERROR: " + prefix, outfile=sys.stderr)

    def log(self, msg: str, pri: int=2, prefix: str=None, outfile=sys.stdout, sep: str=":"):
        """
        This method prints messages to standard output, depending on the priority argument and the
        verbosity level determined from environment variables and CLI switches.

        Invocation with

        * `pri=2` (which is the default) will always print the attached message
        * `pri=1` will print messages when verbosity is set to 1
        * `pri=0` will print messages when verbosity is set to 0 or when debugging is enabled

        Arguments:
            str msg: message that will be printed
            int pri: message priority (0-2, where 0 is lowest and 2 is highest)
        """

        if sep != ":":
            assert isinstance(sep, str)

        if (pri >= self.verby) or self.debug:

            if prefix is not None:
                print(prefix + sep + " " + msg, file=outfile)
                return

            if self.log_prefix is not None:
                print(self.log_prefix + sep + " " + msg, file=outfile)
                return

            print(msg, file=outfile)

    def log_command(self, cmdlist: list, pri: int=2, prefix: str=None):
        """
        This method prints commands that are then executed by use of the :py:func:`subprocess.call`
        or :py:func:`subprocess.check_output` functions. Its priority behaviour is the same as the
        :py:meth:`Kentauros.log` function's.

        Arguments:
            list cmdlist:   list of strings, as passed to :py:mod:`subprocess` functions
            int pri:        message priority (0-2, where 0 is lowest and 2 is highest)
            str prefix:     custom module-wide prefix string
        """

        assert isinstance(cmdlist, list)
        assert isinstance(pri, int)

        if prefix is not None:
            assert isinstance(prefix, str)

        cmdstring = ""

        for cmd in cmdlist:
            assert isinstance(cmd, str)
            cmdstring += (cmd + " ")

        basename = str(cmdlist[0])

        if prefix is not None:
            spacing = " " * len(prefix)
            self.log(basename + " command:", pri, prefix)
            self.log(cmdstring, pri, spacing)
            return

        if self.log_prefix is not None:
            spacing = " " * len(self.log_prefix)
            self.log(basename + " command:", pri)
            self.log(cmdstring, pri, spacing)
            return

    def log_list(self, header: str, lst: list, pri: int=2, prefix: str=None):
        """
        This method prints lists, with one element on each line. Its priority behaviour is the same
        as the :py:meth:`Kentauros.log` function's.

        Arguments:
            str header: header for the list
            list lst:   list of objects that are parseable to str()s by python
            int pri:    message priority (0-2, where 0 is lowest and 2 is highest)
            str prefix: custom module-wide prefix string
        """

        assert isinstance(header, str)
        assert isinstance(lst, list)
        assert isinstance(pri, int)

        if prefix is not None:
            assert isinstance(prefix, str)

        if prefix is not None:
            spacing = " " * len(prefix)
            self.log(header + ":", pri, prefix)

            for element in lst:
                self.log(str(element), pri, spacing, sep="  -")

            return

        if self.log_prefix is not None:
            spacing = " " * len(self.log_prefix)
            self.log(header + ":", pri)

            for element in lst:
                self.log(str(element), pri, spacing, sep="  -")

            return
