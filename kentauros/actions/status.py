"""
This submodule contains the :py:class:`StatusAction` class.
"""


from ..definitions import ActionType
from ..logcollector import LogCollector
from ..result import KtrResult
from ..modules.module import PkgModule

from .abstract import Action


class StatusAction(Action):
    """
    This `Action` subclass contains information for displaying packages which are configured for
    use with kentauros. At the moment, this only includes printing a list of packages, which is done
    by default when kentauros is run. More status messages are plannned for the future.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.STATUS`
    """

    NAME = "Status Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.STATUS

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        """
        This method prints a pretty summary of a package's configuration values to the console.
        Currently, this does nothing whatsoever.
        """

        modules = self.kpkg.get_modules()

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        success = True

        res: KtrResult = self.kpkg.status_string()
        ret.collect(res)
        success = success and res.success

        logger.log(res.value)

        for module in modules:
            assert isinstance(module, PkgModule)
            res = module.status_string()
            ret.collect(res)

            logger.log(res.value)

            success = success and res.success

        return ret.submit(success)
