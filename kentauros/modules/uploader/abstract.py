import abc

from ..module import KtrModule
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult


class Uploader(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.actions["upload"] = self.execute

        # TODO: test "uploader clean all" action
        # TODO: test "uploader status all" action
        # TODO: test "uploader upload all" action
        # TODO: test "uploader verify all" action

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def upload(self) -> KtrResult:
        pass
