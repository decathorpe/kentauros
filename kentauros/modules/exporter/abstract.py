import abc

from ..module import KtrModule
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult


class Exporter(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.actions["export"] = self.execute

    @abc.abstractmethod
    def export(self) -> KtrResult:
        pass
