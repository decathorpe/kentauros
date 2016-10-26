"""
This module contains the abstract :py:class:`Constructor` class, which is then inherited by actual
constructors.
"""


import abc
import os

from kentauros.instance import Kentauros
from kentauros.modules.module import PkgModule


LOG_PREFIX = "ktr/constructor"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class Constructor(PkgModule, metaclass=abc.ABCMeta):
    """
    This class is the abstract base class for all constructors. It's only real function is to
    provide a unified API for builder classes and store the package to which the builder belongs.

    Arguments:
        Package package:    package for which this constructor is for

    Attributes:
        Package cpkg:       stores parent package instance reference
    """

    def __init__(self, package):
        ktr = Kentauros()

        if ktr.debug:
            from kentauros.package import Package
            assert isinstance(package, Package)

        self.cpkg = package
        self.pdir = os.path.join(ktr.conf.get_packdir(), self.cpkg.get_conf_name())

    @abc.abstractmethod
    def status(self) -> dict:
        """
        This method is expected to return a dictionary of statistics about the respective
        constructor.
        """

    @abc.abstractmethod
    def init(self):
        """
        This method creates the directory structure needed by other methods of this class.
        """

    @abc.abstractmethod
    def prepare(self) -> bool:
        """
        This method prepares all files necessary for the actual assembly of the source package.
        """

    @abc.abstractmethod
    def build(self):
        """
        This method assembles the source package from files prepared previously.
        """

    @abc.abstractmethod
    def export(self):
        """
        This method exports the assembled source packages to the specified package directory.
        """

    @abc.abstractmethod
    def cleanup(self):
        """
        This method cleans up all temporary files and directories.
        """
