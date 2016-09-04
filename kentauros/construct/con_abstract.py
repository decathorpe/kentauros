"""
This module contains the abstract :py:class:`Builder` class, which
is then inherited by actual constructors.
"""


import abc


class Constructor(metaclass=abc.ABCMeta):
    """
    This class is the abstract base class for all constructors. It's only real
    function is to provide a unified API for builder classes and store the
    package to which the builder belongs.

    Arguments:
        Package package: package for which this constructor is for

    Attributes:
        Package pkg: stores parent package instance reference
    """

    def __init__(self, package):
        self.pkg = package

    @abc.abstractmethod
    def init(self):
        """
        This method creates the directory structure needed by other methods of
        this class.
        """

    @abc.abstractmethod
    def prepare(self, relreset: bool=False, force: bool=False) -> bool:
        """
        This method prepares all files necessary for the actual assembly of the
        source package.
        """

    @abc.abstractmethod
    def build(self):
        """
        This method assembles the source package from files prepared previously.
        """

    @abc.abstractmethod
    def export(self):
        """
        This method exports (moves) the assembled source packages to the
        specified package directory.
        """

    @abc.abstractmethod
    def clean(self):
        """
        This method cleans up all temporary files and directories.
        """
