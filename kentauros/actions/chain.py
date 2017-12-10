"""
This submodule contains the :py:class:`ChainAction` class.
"""


from ..definitions import ActionType
from ..logcollector import LogCollector
from ..modules.module import PkgModule
from ..result import KtrResult

from .abstract import Action


class ChainAction(Action):
    """
    This :py:class:`Action` subclass contains information for executing a "chain reaction" on the
    package specified at initialisation, which means the following:

    - get sources if they don't already exist (``GetAction``)
    - update sources (``UpdateAction``)
    - if sources already existed, no updates were available and ``--force`` was not specified,
      action execution will terminate at this point and return ``False``
    - otherwise, sources are exported (if tarball doesn't already exist) (``ExportAction``)
    - construct source package (``ConstructAction``), terminate chain if not successful
    - build source package locally (``BuildAction``), terminate chain if not successful
    - upload source package to cloud build service (``UploadAction``)

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.CHAIN``
    """

    NAME = "Chain Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CHAIN

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        """
        This method runs the "chain reaction" corresponding to the package specified at
        initialisation, with the configuration from the package configuration file.

        Returns:
            bool:   ``True`` if chain went all the way through, ``False`` if not
        """

        logger = LogCollector(self.name())

        success = True

        for module in self.kpkg.get_modules():
            assert isinstance(module, PkgModule)

            res: KtrResult = module.execute()
            logger.merge(res.messages)

            if not res.success:
                logger.log("Execution of module unsuccessful: " + str(module))
                success = False
                break

        if success:
            self.update_status()
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return KtrResult(success, logger)
