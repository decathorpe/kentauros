from .meta_state import KtrState


class KtrTestState(KtrState):
    def __init__(self, values: dict = None):
        if values is None:
            values = dict()

        self.values = values

    def read(self, conf_name: str):
        return self.values[conf_name]

    def write(self, conf_name: str, entries: dict):
        old = self.values[conf_name]
        new = entries

        for key in old:
            self.values[conf_name][key] = old[key]

        for key in new:
            self.values[conf_name][key] = new[key]

    def remove(self, conf_name):
        self.values.pop(conf_name)
