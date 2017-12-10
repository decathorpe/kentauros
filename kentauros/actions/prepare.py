"""
This submodule contains the :py:class:`PrepareAction` class.
"""


from ..definitions import ActionType
from ..logcollector import LogCollector
from ..result import KtrResult
from ..modules.module import PkgModule

from .abstract import Action


class PrepareAction(Action):
    """
    This `Action` subclass contains information for preparing the package's sources. Sources will be
    downloaded or copied to destination, updated if already there, and exported to a tarball, if
    necessary.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.PREPARE`
    """

    NAME = "Prepare Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.PREPARE

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        """
        This method executes the :py:meth:`Source.prepare()` method to execute source preparation.
        This includes downloading or copying to destination, updating if necessary, and exporting to
        tarball if necessary.

        Returns:
            bool:           *True* when successful, *False* if sub-action fails
        """

        logger = LogCollector(self.name())

        source: PkgModule = self.kpkg.get_module("source")

        if source is None:
            logger.log("This package doesn't define a source module. Aborting.")
            return KtrResult(True, logger)

        res: KtrResult = source.execute()
        logger.merge(res.messages)

        if res.success:
            self.update_status()
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return KtrResult(res.success, logger)
