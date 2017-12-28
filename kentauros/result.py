from .logcollector import LogCollector


class KtrResult:
    def __init__(self, success: bool = True, value=None,
                 messages: LogCollector = None, state: dict = None, name: str = None):

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
        self.success = self.success and result.success

        self.messages.merge(result.messages)

        for key in result.state.keys():
            self.state[key] = result.state[key]

    def submit(self, success: bool) -> 'KtrResult':
        assert isinstance(success, bool)
        self.success = success

        return self
