import enum
import sys


class LogMessageType(enum.Enum):
    NORMAL = 0
    ERROR = 1
    WARNING = 2
    DEBUG = 3


class LogMessage:
    def __init__(self, log_type: LogMessageType, message: str, origin: str = ""):
        self.log_type = log_type
        self.message = message
        self.origin = origin

    def format(self) -> str:
        if self.origin == "":
            return self.message
        else:
            return "{}: {}".format(self.origin, self.message)


class LogCollector:
    def __init__(self, origin=""):
        self.messages = list()
        self.origin = origin

    def log(self, message: str, origin: str = None):
        if origin is None:
            origin = self.origin
        self.messages.append(LogMessage(LogMessageType.NORMAL, message, origin))

    def cmd(self, command: list, origin: str = None):
        cmd = " ".join(command)
        if origin is None:
            origin = self.origin
        self.messages.append(LogMessage(LogMessageType.DEBUG, "CLI Command: " + cmd, origin))

    def lst(self, title: str, entries: list, origin: str = None):
        if origin is None:
            origin = self.origin

        self.messages.append(LogMessage(LogMessageType.NORMAL, title))
        for entry in entries:
            self.messages.append(LogMessage(LogMessageType.NORMAL, " - " + entry, origin))

    def err(self, message: str, origin: str = None):
        if origin is None:
            origin = self.origin
        self.messages.append(LogMessage(LogMessageType.ERROR, message, origin))

    def dbg(self, message: str, origin: str = None):
        if origin is None:
            origin = self.origin

        self.messages.append(LogMessage(LogMessageType.DEBUG, message, origin))

    def collect(self):
        return self.messages

    def merge(self, logs: 'LogCollector'):
        assert isinstance(logs, LogCollector)
        self.messages.extend(logs.messages)

    def print_all(self, warnings: bool = False, debug: bool = False, dest=None):
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

            print(message.format(), file=print_dest, flush=True)
