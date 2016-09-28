"""
This submodule contains the quasi-abstract :py:class:`Action` class, which is inherited by specific
action implementations.
"""


import abc

from kentauros.instance import Kentauros


class Action(metaclass=abc.ABCMeta):
    """
    This class is the base class for all defined actions. For every action that can be specified at
    ktr command line, there is an Action subclass.

    Arguments:
        str pkg_name:       Package instance this action will be run on

    Attributes:
        str name:           stores the package configuration name given at initialisation
        Package kpkg:       stores reference to the package object
        ActionType atype:   stores type of action as enum
    """

    def __init__(self, pkg_name: str):
        assert isinstance(pkg_name, str)

        ktr = Kentauros()

        self.name = pkg_name
        self.kpkg = ktr.get_package(pkg_name)
        assert self.kpkg is not None

        self.atype = None

    @abc.abstractmethod
    def execute(self):
        """
        This method runs the action corresponding to the :py:class:`Action` instance on the package
        specified at initialisation. It is overridden by subclasses to contain the real code for the
        action.
        """
