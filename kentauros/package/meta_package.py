import abc
import enum
import os

from ..context import KtrContext
from ..result import KtrResult


class ReleaseType(enum.Enum):
    STABLE = 0
    POST = 1
    PRE = 2


class KtrMetaPackage(metaclass=abc.ABCMeta):
    def __init__(self, context: KtrContext, conf_name: str):
        assert isinstance(context, KtrContext)
        assert isinstance(conf_name, str)

        self.context = context
        self.conf_name = conf_name

        self.conf_path = os.path.join(self.context.get_confdir(), self.conf_name + ".conf")

    @abc.abstractmethod
    def get_version(self) -> str:
        pass

    @abc.abstractmethod
    def get_release_type(self) -> ReleaseType:
        pass

    @abc.abstractmethod
    def get_version_separator(self) -> str:
        pass

    @abc.abstractmethod
    def replace_vars(self, input_str: str) -> str:
        pass

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def status_string(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def verify(self) -> KtrResult:
        pass
