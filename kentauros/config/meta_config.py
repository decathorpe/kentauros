import abc
import configparser as cp


class KtrConfigError(Exception):
    def __init__(self, value: str = ""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class KtrConfig(metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()

        self.conf: cp.ConfigParser = None

    @abc.abstractmethod
    def get(self, section: str, key: str):
        pass

    @abc.abstractmethod
    def getboolean(self, section: str, key: str):
        pass
