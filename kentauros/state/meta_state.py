import abc


class KtrMetaState(metaclass=abc.ABCMeta):
    def __init__(self, path: str):
        assert isinstance(path, str)
        self.path = path

    @abc.abstractmethod
    def read(self, conf_name: str) -> dict:
        pass

    @abc.abstractmethod
    def write(self, conf_name: str, entries: dict):
        pass

    @abc.abstractmethod
    def remove(self, conf_name):
        pass
