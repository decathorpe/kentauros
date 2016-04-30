"""
This submodule contains the :py:class:`Kentauros` class, which holds
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


def __smaller_int__(int1: int, int2: int):
    if int1 < int2:
        return int1
    else:
        return int2


# TODO: remove old log,dbg,err functions


class Kentauros:
    """
    This class stores settings and variables that must be the same during the
    execution of code from the "kentauros" package. This is accomplished by
    storing the critical data in a class variable, which is initialised only
    once per execution.

    It also provides methods for printing log, error and debug messages to
    standard output or error output.

    Attributes:
        dict saved_state:   stores critical values during the kentauros python
                            package execution

    Arguments:
        InstanceType itype: type of kentauros instance (normal, config, create)
    """

    saved_state = dict()

    def __getattr__(self, attr: str):
        return self.saved_state.__getitem__(attr)


    def __setattr__(self, attr: str, val):
        self.saved_state.__setitem__(attr, val)


    def __init__(self, itype: InstanceType=InstanceType.NORMAL):
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


    def dbg(self, msg: str):
        """
        This method prints messages with a "DEBUG: " prefix to stdout, but
        only if the ``KTR_DEBUG`` environment variable has been set or the
        ``--debug`` or ``-d`` flag has been supplied to the CLI.

        Arguments:
            str msg: debug message to be printed
        """

        if self.debug:
            print("DEBUG: " + str(msg))


    def err(self, msg: str):
        """
        This method prints messages with an "ERROR: " prefix to standard error
        output, regardless of environment variables and CLI settings supplied.

        Arguments:
            str msg: error message to be printed
        """

        self.log("ERROR: " + msg, 2, sys.stderr)


    def log(self, msg: str, pri: int=2, outfile=sys.stdout):
        """
        This method prints messages to standard output, depending on the
        priority argument and the verbosity level determined from environment
        variables and CLI switches.

        Invocation with

        * ``pri=2`` (which is the default) will always print the attached
          message
        * ``pri=1`` will print messages when verbosity is set to 1
        * ``pri=0`` will print messages when verbosity is set to 0 or when
          debugging is enabled

        Arguments:
            str msg: message that will be printed
            int pri: message priority (0-2, where 0 is lowest and 2 is highest)
        """

        if (pri >= self.verby) or self.debug:
            print(msg, file=outfile)


    def log_command(self, prefix1: str, basename: str,
                    cmdlist: list, pri: int=2):
        """
        This method prints commands that are then executed by use of the
        :py:func:`subprocess.call` or :py:func:`subprocess.check_output`
        functions. Its priority behaviour is the same as the :py:func:`log`
        function's.

        Arguments:
            str prefix1:    module-wide prefix string
            str basename:   command base name
            list cmdlist:   list of strings, as passed to :py:mod:``subprocess``
                            functions
            int pri:        message priority (0-2, where 0 is lowest and 2 is
                            highest)
        """

        cmdstr = ""
        prefix2 = " " * len(prefix1)

        for cmd in cmdlist:
            cmdstr += (cmd + " ")

        self.log(prefix1 + basename + " command:", pri)
        self.log(prefix2 + cmdstr, pri)


def dbg(msg: str):
    """
    This function prints messages with a "DEBUG: " prefix to standard output,
    but only if the ``KTR_DEBUG`` environment variable has been set or the
    ``--debug`` or ``-d`` has been supplied to the calling script.

    Arguments:
        str msg: debug message to be printed
    """

    if Kentauros().debug:
        print("DEBUG: " + str(msg))


def err(msg: str):
    """
    This function prints messages with an "ERROR: " prefix to standard error
    output, regardless of environment variables and CLI settings supplied.

    Arguments:
        str msg: error message to be printed
    """

    print("ERROR: " + msg, file=sys.stderr)


def log(msg: str, pri: int=2):
    """
    This function prints messages to standard output, depending on the priority
    argument and the verbosity level determined from environment variables and
    CLI switches.

    Invocation with

    * ``pri=2`` (which is the default) will always print the attached message
    * ``pri=1`` will print messages when verbosity is set to 1
    * ``pri=0`` will print messages when verbosity is set to 0 or when debugging
      is enabled

    Arguments:
        str msg: message that will be printed
        int pri: message priority (0-2, where 0 is lowest and 2 is highest)
    """

    if (pri >= Kentauros().verby) or Kentauros().debug:
        print(msg)


def log_command(prefix1: str, basename: str, cmdlist: list, pri: int=2):
    """
    This function prints commands that are then executed by use of the
    :py:func:`subprocess.call` or :py:func:`subprocess.check_output` functions.
    Its priority behaviour is the same as the :py:func:`log` function's.

    Arguments:
        str prefix1:  module-wide prefix string
        str basename: command base name
        list cmdlist: list of strings, as passed to :py:mod:``subprocess``
                      functions
        int pri:      message priority (0-2, where 0 is lowest and 2 is highest)
    """

    cmdstr = ""
    prefix2 = " " * len(prefix1)

    for cmd in cmdlist:
        cmdstr += (cmd + " ")

    log(prefix1 + basename + " command:", pri)
    log(prefix2 + cmdstr, pri)

