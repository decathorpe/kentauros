"""
This module contains the abstract :py:class:`PkgModule` class, defines the methods all package
modules must provide.
"""


import abc


class PkgModule(metaclass=abc.ABCMeta):
    """
    This abstract class defines the properties that all package modules must have.
    """

    # @abc.abstractmethod
    # def execute(self) -> bool:
    #     """
    #     This method is expected to execute the package module and return a boolean, indicating
    #     whether the execution finished successfully or not.
    #     """

    @abc.abstractmethod
    def status(self) -> dict:
        """
        This method is expected to return a dictionary of statistics about this module.
        """

    @abc.abstractmethod
    def verify(self) -> bool:
        """
        This method checks if all configuration values needed for this module are present and valid.
        """
