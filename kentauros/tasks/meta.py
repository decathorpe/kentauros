import abc

from ..result import KtrResult


class KtrMetaTask(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self) -> KtrResult:
        pass
