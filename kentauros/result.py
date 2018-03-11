class KtrResult:
    def __init__(self, success: bool = True, value=None, state: dict = None):

        assert isinstance(success, bool)
        self.success = success

        self.value = value

        if state is None:
            self.state = dict()
        else:
            assert isinstance(state, dict)
            self.state = state

    def collect(self, result: 'KtrResult'):
        self.success = self.success and result.success

        for key in result.state.keys():
            self.state[key] = result.state[key]

    def submit(self, success: bool) -> 'KtrResult':
        assert isinstance(success, bool)
        self.success = success

        return self
