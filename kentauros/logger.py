"""
This submodule contains the KtrLogger class, which provides methods for logging messages to file or
standard outputs.
"""


import sys

from kentauros.instance import Kentauros


LOGPREFIX = "ktr/logger"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


def print_flush(*args, **kwargs):
    """
    This function serves as a wrapper around the built-in print function. Calling it instead
    of the standard `print` ensures that output buffers are flushed after every call.
    """

    print(*args, **kwargs, flush=True)


class KtrLogger:
    """
    This class provides methods for printing messages to standard outputs.

    Arguments:
        log_prefix: specifies a custom prefix for log messages

    Attributes:
        log_prefix: stores a custom prefix for log messages
    """

    def __init__(self, log_prefix: str=None):
        if log_prefix is not None:
            assert isinstance(log_prefix, str)

        self.log_prefix = log_prefix

    def dbg(self, msg: str, prefix: str=None):
        """
        This method prints messages with a "DEBUG: " prefix to stdout, but only if the *KTR_DEBUG*
        environment variable has been set or the `--debug` or `-d` flag has been supplied at the
        command line.

        Arguments:
            str msg:    debug message to be printed
        """

        ktr = Kentauros()

        if not ktr.debug:
            return

        assert isinstance(msg, str)

        if prefix is not None:
            print_flush("DEBUG: " + prefix + " " + msg)
            return

        if self.log_prefix is not None:
            print_flush("DEBUG: " + self.log_prefix + " " + msg)
            return

        print_flush("DEBUG: " + msg)

    def err(self, msg: str, prefix: str=None):
        """
        This method prints messages with an "ERROR: " prefix to standard error output, regardless
        of environment variables and CLI settings supplied.

        Arguments:
            str msg:    error message to be printed
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
            str msg:    message that will be printed
            int pri:    message priority (0-2, where 0 is lowest and 2 is highest)
        """

        if sep != ":":
            assert isinstance(sep, str)

        ktr = Kentauros()

        if (pri >= ktr.verby) or ktr.debug:

            if prefix is not None:
                print_flush(prefix + sep + " " + msg, file=outfile)
                return

            if self.log_prefix is not None:
                print_flush(self.log_prefix + sep + " " + msg, file=outfile)
                return

            print_flush(msg, file=outfile)

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
