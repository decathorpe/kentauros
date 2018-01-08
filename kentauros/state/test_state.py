from .meta_state import KtrState


class KtrTestState(KtrState):
    def __init__(self):
        pass

    def read(self, conf_name: str):
        # TODO
        pass

    def write(self, conf_name: str, entries: dict):
        # TODO
        pass

    def remove(self, conf_name):
        # TODO
        pass
