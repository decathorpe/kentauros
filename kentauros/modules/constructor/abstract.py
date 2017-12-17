"""
This module contains the abstract :py:class:`Constructor` class, which is then inherited by actual
constructors.
"""


import abc
import os

from ...context import KtrContext
from ...modules.module import KtrModule
from ...package import KtrPackage
from ...result import KtrResult


class Constructor(KtrModule, metaclass=abc.ABCMeta):
    """
    This class is the abstract base class for all constructors. It's only real function is to
    provide a unified API for builder classes and store the package to which the builder belongs.

    Arguments:
        Package package:    package for which this constructor is for

    Attributes:
        Package cpkg:       stores parent package instance reference
    """

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.pdir = os.path.join(self.context.get_packdir(), self.package.conf_name)
        self.actions["build"] = self.execute

    @abc.abstractmethod
    def status(self) -> KtrResult:
        """
        This method is expected to return a dictionary of statistics about the respective
        constructor.
        """

    @abc.abstractmethod
    def init(self) -> KtrResult:
        """
        This method creates the directory structure needed by other methods of this class.
        """

    @abc.abstractmethod
    def prepare(self) -> KtrResult:
        """
        This method prepares all files necessary for the actual assembly of the source package.
        """

    @abc.abstractmethod
    def build(self) -> KtrResult:
        """
        This method assembles the source package from files prepared previously.
        """

    @abc.abstractmethod
    def export(self) -> KtrResult:
        """
        This method exports the assembled source packages to the specified package directory.
        """

    @abc.abstractmethod
    def cleanup(self) -> KtrResult:
        """
        This method cleans up all temporary files and directories.
        """
