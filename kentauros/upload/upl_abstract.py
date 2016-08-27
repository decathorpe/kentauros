"""
This module contains the template / dummy :py:class:`Uploader` class, which
is then inherited by actual uploaders.
"""


import abc


class Uploader(metaclass=abc.ABCMeta):
    """
    This class serves as a quasi-abstract base class for source package
    uploaders. They are expected to override this class's methods as
    necessary.

    Arguments:
        Package package:    package for which this constructor is for

    Attributes:
        Package upkg:       stores parent package instance reference
    """

    def __init__(self, package):
        self.upkg = package

    @abc.abstractmethod
    def upload(self):
        """
        This method executes the source package upload with the settings
        specified in the package configuration.
        """
