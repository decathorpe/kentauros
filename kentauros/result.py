"""
This module contains the common result type used in kentauros.
"""

from .logcollector import LogCollector


class KtrResult:
    """
    This class is the common result type used in kentauros, and it encapsulates a success value
    (`True` or `False`), a return value, a return type, the log messages collected by the returning
    method or function, and status updates, if available.

    Arguments:
        bool success:           flag indicating successful execution
        value:                  optional return value
        LogCollector messages:  collected log messages
        dict state:             collected global state changes
    """

    def __init__(self,
                 success: bool = True,
                 value=None,
                 messages: LogCollector = None,
                 state: dict = None,
                 name: str = None):

        assert isinstance(success, bool)
        self.success = success

        self.value = value

        if messages is None:
            if name is not None:
                assert isinstance(name, str)
                self.messages = LogCollector(name)
            else:
                self.messages = LogCollector()
        else:
            assert isinstance(messages, LogCollector)
            self.messages = messages

        if state is None:
            self.state = dict()
        else:
            assert isinstance(state, dict)
            self.state = state

    def collect(self, result: 'KtrResult'):
        """
        This method collects log messages and accumulated global state changes from another result.
        It does *not* set the return value, however.

        Arguments:
            KtrResult result:   result to merge into this instance
        """

        self.success = self.success and result.success

        self.messages.merge(result.messages)

        for key in result.state.keys():
            self.state[key] = result.state[key]

    def submit(self, success: bool) -> 'KtrResult':
        """
        This method sets the `success` flag and returns the instance itself. This is intended to be
        used in return statements.

        Arguments:
            bool success:   flag indicating successful execution

        Returns:
            KtrResult:      result with `success` flag set accordingly
        """

        assert isinstance(success, bool)
        self.success = success

        return self
