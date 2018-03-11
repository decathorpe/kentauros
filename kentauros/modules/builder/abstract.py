import abc
import logging
import os
import shutil

from kentauros.context import KtrContext
from kentauros.modules.module import KtrModule
from kentauros.package import KtrPackage
from kentauros.result import KtrResult


class Build(metaclass=abc.ABCMeta):
    def __init__(self, path: str, dist: str, context: KtrContext):
        self.path = path
        self.dist = dist
        self.context = context

    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def build(self) -> KtrResult:
        pass


class Builder(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.edir = os.path.join(self.context.get_expodir(), self.package.conf_name)
        self.pdir = os.path.join(self.context.get_packdir(), self.package.conf_name)

        self.actions["build"] = self.execute
        self.actions["lint"] = self.lint

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def build(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def export(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def lint(self) -> KtrResult:
        pass

    def clean(self) -> KtrResult:
        if not os.path.exists(self.edir):
            return KtrResult(True)

        ret = KtrResult()
        logger = logging.getLogger("ktr/builder")

        try:
            assert self.context.get_expodir() in self.edir
            assert os.path.isabs(self.edir)
            shutil.rmtree(self.edir)
            return ret.submit(True)
        except AssertionError:
            logger.error("The Package exports directory looks weird. Doing nothing.")
            return ret.submit(False)
        except OSError:
            logger.error("The Package exports directory couldn't be removed.")
            return ret.submit(False)
