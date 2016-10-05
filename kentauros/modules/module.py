"""
This module contains the abstract :py:class:`PkgModule` class, defines the methods all package
modules must provide.
"""


import abc


class PkgModule(metaclass=abc.ABCMeta):
    """
    This abstract class defines the properties that all package modules must have.
    """

    @abc.abstractmethod
    def __str__(self) -> str:
        """
        This method is expected to produce a nice string describing the submodule.

        Returns:
             str:   string containing a description of the submodule
        """

    @abc.abstractmethod
    def execute(self) -> bool:
        """
        This method is expected to execute the package module and return a boolean, indicating
        whether the execution finished successfully or not.

        Returns:
            bool:   boolean indicating whether the execution was successful
        """

    @abc.abstractmethod
    def clean(self) -> bool:
        """
        This method is expected to clean up a submodule's files and folders, if it creates any
        during its execution.

        Returns:
            bool:   boolean indicating whether cleaning up was successful
        """

    @abc.abstractmethod
    def status(self) -> dict:
        """
        This method is expected to return a dictionary of statistics about this module.

        Returns:
            dict:   dictionary containing the submodule's exported stats
        """

    @abc.abstractmethod
    def verify(self) -> bool:
        """
        This method checks if all configuration values needed for this module are present and valid.

        Returns:
            bool:   boolean indicating whether the configuration / system verification completed
                    successfully
        """
