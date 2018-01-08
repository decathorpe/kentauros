import abc
import os

from ..config import KtrConfig
from ..state import KtrState


class KtrContext(metaclass=abc.ABCMeta):
    def __init__(self, basedir: str, conf_path: str):
        assert isinstance(basedir, str)
        assert isinstance(conf_path, str)

        if not os.path.exists(basedir):
            raise FileNotFoundError(
                "The specified base directory ({}) could not be found.".format(basedir))

        if not os.path.exists(conf_path):
            raise FileNotFoundError(
                "The specified kentaurosrc file ({}) could not be found.".format(conf_path))

        self.basedir = basedir
        self.conf_path = conf_path

        self.state = KtrState(os.path.join(self.basedir, "state.json"))
        self.conf = KtrConfig(conf_path)

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
    def warnings(self) -> bool:
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
