"""
This module contains the abstract :py:class:`Uploader` class, which is then inherited by actual
upload classes.
"""


import abc

from kentauros.modules.module import PkgModule


class Uploader(PkgModule, metaclass=abc.ABCMeta):
    """
    This class serves as a quasi-abstract base class for source package uploader classes. They are
    expected to override this class's methods as necessary.

    Arguments:
        Package package:    package for which this constructor is for

    Attributes:
        Package upkg:       stores parent package instance reference
    """

    def __init__(self, package):
        self.upkg = package

    @abc.abstractmethod
    def status(self) -> dict:
        """
        This method is expected to return a dictionary of statistics about the respective uploader.
        """

    @abc.abstractmethod
    def upload(self):
        """
        This method executes the source package upload with the settings specified in the package
        configuration.
        """
