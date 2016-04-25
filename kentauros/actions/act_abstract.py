"""
This submodule contains the quasi-abstract :py:class:`Action` class, which is
inherited by specific action implementations.
"""


import abc

from kentauros.package import Package


class Action(metaclass=abc.ABCMeta):
    """
    This class is the base class for all defined actions. For every action that
    can be specified at ktr command line, there is an Action subclass.

    Arguments:
        Package kpkg:       Package instance this action will be run on
        bool force:         specifies if the pending action should be forced

    Attributes:
        Package kpkg:       stores reference to package given at initialisation
        bool force:         stores force value given at initialisation
        ActionType atype:   stores type of action as enum
    """

    def __init__(self, kpkg: Package, force: bool):
        assert isinstance(kpkg, Package)
        assert isinstance(force, bool)

        self.kpkg = kpkg
        self.force = force
        self.atype = None

    @abc.abstractmethod
    def execute(self):
        """
        This method runs the action corresponding to the :py:class:`Action`
        instance on the package specified at initialisation. It is overridden by
        subclasses to contain the real code for the action.
        """

