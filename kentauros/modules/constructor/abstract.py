import abc
import os

from kentauros.context import KtrContext
from kentauros.modules.module import KtrModule
from kentauros.package import KtrPackage
from kentauros.result import KtrResult


class Constructor(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.pdir = os.path.join(self.context.get_packdir(), self.package.conf_name)

        self.actions["build"] = self.build
        self.actions["increment"] = self.increment
        self.actions["lint"] = self.lint

    @abc.abstractmethod
    def build(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def increment(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def lint(self) -> KtrResult:
        pass
