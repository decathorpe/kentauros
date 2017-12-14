"""
This submodule contains the quasi-abstract :py:class:`Action` class, which is inherited by specific
action implementations.
"""


import abc

from ..instance import Kentauros
from ..modules.module import PkgModule
from ..oldpackage import OldPackage
from ..result import KtrResult


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
        self.kpkg = ktr.get_package(pkg_name)

        assert self.kpkg is not None
        assert isinstance(self.kpkg, OldPackage)

        self.atype = None

    @abc.abstractmethod
    def name(self) -> str:
        """This method returns a concise name of the module."""

    @abc.abstractmethod
    def execute(self) -> KtrResult:
        """
        This method runs the action corresponding to the :py:class:`Action` instance on the package
        specified at initialisation. It is overridden by subclasses to contain the real code for the
        action. Also, it is expected that actions update the package database after they have
        finished successfully.
        """

    def update_status(self) -> KtrResult:
        """
        This method writes a package's and all its sub-module's status to the package database. It
        is executed after actions.
        """

        modules = self.kpkg.get_modules()

        ret = KtrResult()
        ret.collect(self.kpkg.status())

        success = True

        for module in modules:
            assert isinstance(module, PkgModule)

            res = module.status()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

    def import_status(self) -> KtrResult:
        """
        This method imports a package's and all its sub-module's status to the package database.
        """

        modules = self.kpkg.get_modules()

        ret = KtrResult()
        ret.collect(self.kpkg.status())

        success = True

        for module in modules:
            assert isinstance(module, PkgModule)

            res = module.imports()

            ret.collect(res)
            success = success and res.success

        return ret.submit(success)
