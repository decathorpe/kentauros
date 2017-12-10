"""
This submodule contains the :py:class:`ConstructAction` class.
"""


from ..definitions import ActionType
from ..logcollector import LogCollector
from ..result import KtrResult
from ..modules.module import PkgModule

from .abstract import Action


class ConstructAction(Action):
    """
    This :py:class:`Action` subclass contains information for constructing the source package from
    sources and package specification for the package specified at initialisation.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.CONSTRUCT``
    """

    NAME = "Construct Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CONSTRUCT

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        logger = LogCollector(self.name())

        constructor: PkgModule = self.kpkg.get_module("constructor")

        if constructor is None:
            logger.log("This package doesn't define a constructor module. Aborting.")
            return KtrResult(True, logger)

        res = constructor.execute()
        logger.merge(res.messages)

        if res.success:
            self.update_status()
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return KtrResult(res.success, logger)
