import abc
import os

from ...context import KtrContext
from ...modules.module import KtrModule
from ...package import KtrPackage
from ...result import KtrResult


class Constructor(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.pdir = os.path.join(self.context.get_packdir(), self.package.conf_name)
        self.actions["build"] = self.execute

        # TODO: test "constructor build all" action
        # TODO: test "constructor clean all" action
        # TODO: test "constructor status all" action
        # TODO: test "constructor verify all" action

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def build(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def export(self) -> KtrResult:
        pass

    # TODO: add "update" action?
