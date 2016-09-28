"""
This submodule contains the :py:class:`ChainAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.actions.act_abstract import Action
from kentauros.actions.act_common import LOGPREFIX
from kentauros.actions.act_build import BuildAction
from kentauros.actions.act_construct import ConstructAction
from kentauros.actions.act_export import ExportAction
from kentauros.actions.act_get import GetAction
from kentauros.actions.act_update import UpdateAction
from kentauros.actions.act_upload import UploadAction
from kentauros.actions.act_verify import VerifyAction


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

        def print_abort_msg():
            """This function prints a standard abort message."""
            logger.log("Action aborted.", 2)

        verified = VerifyAction(self.name).execute()
        if not verified:
            print_abort_msg()
            return False

        get = GetAction(self.name).execute()
        if not get:
            logger.log("Sources not downloaded.", 2)

        update = UpdateAction(self.name).execute()
        if not update:
            logger.log("Sources not updated.", 2)

        if not (get or update or force):
            logger.log("No source changes were detected, aborting action.", 2)
            return False

        ExportAction(self.name).execute()

        success = ConstructAction(self.name).execute()
        if not success:
            print_abort_msg()
            return False

        success = BuildAction(self.name).execute()
        if not success:
            print_abort_msg()
            return False

        UploadAction(self.name).execute()

        return True
