"""
This module contains the abstract :py:class:`PkgFormatter` class, which is then inherited by actual
package format helpers.
"""


import abc

from kentauros.instance import Kentauros
from kentauros.modules.module import PkgModule


LOGPREFIX = "ktr/pkgformatter"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class PkgFormatter(PkgModule, metaclass=abc.ABCMeta):
    def __init__(self, package):
        ktr = Kentauros()

        if ktr.debug:
            from kentauros.package import Package
            assert isinstance(package, Package)

        self.fpkg = package

    @abc.abstractmethod
    def status(self) -> dict:
        pass

    @abc.abstractmethod
    def init(self):
        pass

    @abc.abstractmethod
    def prepare(self) -> bool:
        pass

    @abc.abstractmethod
    def build(self):
        pass

    @abc.abstractmethod
    def export(self):
        pass

    @abc.abstractmethod
    def cleanup(self):
        pass
