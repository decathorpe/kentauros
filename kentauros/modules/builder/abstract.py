"""
This module contains the abstract :py:class:`Builder` class, which is then inherited by actual
builders.
"""


import abc
import os

from ...context import KtrContext
from ...modules.module import PkgModule
from ...package import KtrPackage
from ...result import KtrResult


class Builder(PkgModule, metaclass=abc.ABCMeta):
    """
    This class is the base class for all builders. It's only real function is to provide a unified
    API for builder classes and store the package to which the builder belongs.

    Arguments:
        Package package:    package to which this builder belongs

    Attributes:
        Package bpkg:       stores the package argument given at initialisation
    """

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.pdir = os.path.join(self.context.get_packdir(), self.package.conf_name)

    @abc.abstractmethod
    def status(self) -> KtrResult:
        """
        This method is expected to return a dictionary of statistics about the respective builder.
        """

    @abc.abstractmethod
    def build(self) -> KtrResult:
        """
        This method executes the builder commands.
        """

    @abc.abstractmethod
    def export(self) -> KtrResult:
        """
        This method exports the built packages (if any) to the directory
        specified for package exports.
        """
