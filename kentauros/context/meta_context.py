import abc

from kentauros.config import KtrConfig
from kentauros.state import KtrState


class KtrContext(metaclass=abc.ABCMeta):
    def __init__(self):
        self.conf: KtrConfig = None
        self.state: KtrState = None

    @abc.abstractmethod
    def get_force(self) -> bool:
        pass

    @abc.abstractmethod
    def get_logfile(self) -> str:
        pass

    @abc.abstractmethod
    def get_message(self) -> str:
        pass

    @abc.abstractmethod
    def debug(self) -> bool:
        pass

    @abc.abstractmethod
    def get_basedir(self) -> str:
        pass

    @abc.abstractmethod
    def get_confdir(self) -> str:
        pass

    @abc.abstractmethod
    def get_datadir(self) -> str:
        pass

    @abc.abstractmethod
    def get_expodir(self) -> str:
        pass

    @abc.abstractmethod
    def get_packdir(self) -> str:
        pass

    @abc.abstractmethod
    def get_specdir(self) -> str:
        pass
