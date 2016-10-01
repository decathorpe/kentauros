"""
This module contains the abstract :py:class:`Builder` class, which is then inherited by actual
builders.
"""


import abc
import os

from kentauros.instance import Kentauros
from kentauros.modules.module import PkgModule


LOGPREFIX = "ktr/builder"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class Builder(PkgModule, metaclass=abc.ABCMeta):
    """
    This class is the base class for all builders. It's only real function is to provide a unified
    API for builder classes and store the package to which the builder belongs.

    Arguments:
        Package package:    package to which this builder belongs

    Attributes:
        Package package:    stores the package argument given at initialisation
    """

    def __init__(self, package):
        ktr = Kentauros()

        if ktr.debug:
            from kentauros.package import Package
            assert isinstance(package, Package)

        self.bpkg = package
        self.pdir = os.path.join(ktr.conf.get_packdir(), self.bpkg.conf_name)

    @abc.abstractmethod
    def status(self) -> dict:
        """
        This method is expected to return a dictionary of statistics about the respective builder.
        """

    @abc.abstractmethod
    def build(self):
        """
        This method executes the builder commands.
        """

    @abc.abstractmethod
    def export(self):
        """
        This method exports the built packages (if any) to the directory
        specified for package exports.
        """
