import abc


class KtrState(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def read(self, conf_name: str) -> dict:
        pass

    @abc.abstractmethod
    def write(self, conf_name: str, entries: dict):
        pass

    @abc.abstractmethod
    def remove(self, conf_name):
        pass
