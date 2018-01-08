import abc

from kentauros.context import KtrContext
from kentauros.modules.module import KtrModule
from kentauros.package import KtrPackage
from kentauros.result import KtrResult


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
