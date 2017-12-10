"""
This module contains the common result type used in kentauros.
"""

from .logcollector import LogCollector


class KtrResult:
    """
    This class is the common result type used in kentauros, and it encapsulates a success value
    (`True` or `False`), and the log messages collected by the returning method or function.
    """

    def __init__(self, success: bool, messages: LogCollector):
        self.success = success
        self.messages = messages

    @staticmethod
    def true():
        """
        This static method constructs a default `True` result type, with no log messages.

        Returns:
            KtrResult:  empty `True` result
        """

        return KtrResult(True, LogCollector())

    @staticmethod
    def false():
        """
        This static method constructs a default `False` result type, with no log messages.

        Returns:
            KtrResult:  empty `False` result
        """

        return KtrResult(False, LogCollector())
