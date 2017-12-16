"""
This module contains the classes and definitions for the log collection functionality.
"""

import enum
import sys


class LogMessageType(enum.Enum):
    """
    This enum defines the importance of log messages.

    - `NORMAL` messages are supposed to be written to stdout,
    - `ERROR` messages are supposed to be written to stderr,
    - `WARNING` messages are supposed to be written to stdout, but only when enabled, and
    - `DEBUG` messages are supposed to be written to stdout, but only in debug mode.
    """

    NORMAL = 0
    ERROR = 1
    WARNING = 2
    DEBUG = 3


class LogMessage:
    """
    This class encapsulates one log entry, including a type (normal, error, or debug), the message
    text, and an optional message origin (usually the name of the class logging the message).
    """

    def __init__(self, log_type: LogMessageType, message: str, origin: str = ""):
        self.log_type = log_type
        self.message = message
        self.origin = origin

    def format(self) -> str:
        """
        This method formats the message body depending on whether the origin string has been set or
        not.

        Returns:
            str: formatted message string
        """

        if self.origin == "":
            return self.message
        else:
            return "{}: {}".format(self.origin, self.message)


class LogCollector:
    """
    This class encapsulates the (off-console) collection of log messages, which can then be written
    to the console (or a file) at the desired point in time.
    """

    def __init__(self, origin=""):
        self.messages = list()
        self.origin = origin

    def log(self, message: str, origin: str = None):
        """
        This method collects standard log messages, with an optional origin override.

        Arguments:
            str message:    message to log
            str origin:     origin override
        """

        if origin is None:
            origin = self.origin
        self.messages.append(LogMessage(LogMessageType.NORMAL, message, origin))

    def cmd(self, command: list, origin: str = None):
        """
        This method collects CLI commands as standard log messages, with an optional origin
        override.

        Arguments:
            list command:   command array to log
            str origin:     origin override
        """

        cmd = " ".join(command)
        if origin is None:
            origin = self.origin
        self.messages.append(LogMessage(LogMessageType.DEBUG, "CLI Command: " + cmd, origin))

    def lst(self, title: str, entries: list, origin: str = None):
        """
        This method collects lists as standard log messages, with an optional origin override.

        Arguments:
            str title:      header of the list
            list entries:   list entries (list of strings)
            str origin:     origin override
        """

        if origin is None:
            origin = self.origin

        self.messages.append(LogMessage(LogMessageType.NORMAL, title))
        for entry in entries:
            self.messages.append(LogMessage(LogMessageType.NORMAL, " - " + entry, origin))

    def err(self, message: str, origin: str = None):
        """
        This method collects error messages, with an optional origin override.

        Arguments:
            str message:    message to log
            str origin:     origin override
        """

        if origin is None:
            origin = self.origin
        self.messages.append(LogMessage(LogMessageType.ERROR, message, origin))

    def dbg(self, message: str, origin: str = None):
        """
        This method collects debug messages, with an optional origin override.

        Arguments:
            str message:    message to log
            str origin:     origin override
        """

        if origin is None:
            origin = self.origin

        self.messages.append(LogMessage(LogMessageType.DEBUG, message, origin))

    def collect(self):
        """
        This method returns a list of the collected messages.

        Returns:
            list:   all collected log messages
        """

        return self.messages

    def merge(self, logs: 'LogCollector'):
        """
        This method merges another list of log messages into this one.
        """

        assert isinstance(logs, LogCollector)
        self.messages.extend(logs.messages)

    def print(self, warnings: bool = False, debug: bool = False, dest=None):
        """
        This method prints the collected log messages to the appropriate destinations.

        Arguments:
            dest:       destination override (open file, such as `sys.stdout`)
            warnings:   enable printing warnings
            debug:      enable printing debug messages
        """

        default_dest = dict()
        default_dest[LogMessageType.NORMAL] = sys.stdout
        default_dest[LogMessageType.ERROR] = sys.stderr
        default_dest[LogMessageType.WARNING] = sys.stdout
        default_dest[LogMessageType.DEBUG] = sys.stdout

        for message in self.messages:
            assert isinstance(message, LogMessage)

            if message.log_type == LogMessageType.WARNING:
                if (not warnings) or (not debug):
                    continue

            if message.log_type == LogMessageType.DEBUG:
                if not debug:
                    continue

            if dest is None:
                print_dest = default_dest[message.log_type]
            else:
                print_dest = dest

            print(message.format(), file=print_dest)
