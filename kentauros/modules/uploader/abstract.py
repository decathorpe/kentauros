import abc

from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult

from ..module import KtrModule


class Uploader(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.actions["upload"] = self.execute

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def upload(self) -> KtrResult:
        pass
