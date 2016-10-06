"""
This submodule contains the :py:class:`ChainAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.actions.abstract import Action
from kentauros.actions.common import LOGPREFIX


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

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CHAIN

    def execute(self) -> bool:
        """
        This method runs the "chain reaction" corresponding to the package specified at
        initialisation, with the configuration from the package configuration file.

        Returns:
            bool:   ``True`` if chain went all the way through, ``False`` if not
        """

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)
        force = ktr.cli.get_force()

        success = True

        for module in self.kpkg.get_modules():
            succeeded = module.execute()

            if not succeeded:
                logger.err("Execution of module '" + str(module) + "' wasn't successful.")

                if force:
                    logger.log("Execution is forced to continue.")
                    success = success and succeeded
                    continue
                else:
                    success = False
                    break

        self.update_status()

        return success
