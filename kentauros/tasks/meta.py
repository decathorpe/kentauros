import abc

from kentauros.result import KtrResult


class KtrMetaTask(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self) -> KtrResult:
        pass
