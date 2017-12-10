"""
This submodule contains the :py:class:`BuildAction` class.
"""


from ..definitions import ActionType
from ..logcollector import LogCollector
from ..modules.module import PkgModule
from ..result import KtrResult

from .abstract import Action


class BuildAction(Action):
    """
    This :py:class:`Action` subclass contains information for executing a local build of the package
    specified at initialisation.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.BUILD``
    """

    NAME = "Build Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.BUILD

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        logger = LogCollector(self.NAME)

        builder: PkgModule = self.kpkg.get_module("builder")

        if builder is None:
            logger.log("This package doesn't define a builder module. Aborting.")
            return KtrResult(True, logger)

        res = builder.execute()

        if res.success:
            self.update_status()
            logger.merge(res.messages)
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.merge(res.messages)
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return KtrResult(res.success, logger)
