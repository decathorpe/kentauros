"""
This submodule contains the :py:class:`ChainAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.package import Package

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
        Package kpkg:       package this chain reaction will done for
        bool force:         force further actions even if sources did not change

    Attributes:
        ActionType atype:   here: stores ``ActionType.CHAIN``
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.CHAIN

    def execute(self) -> bool:
        """
        This method runs the "chain reaction" corresponding to the package specified at
        initialisation, with the configuration from the package configuration file.

        Returns:
            bool:   ``True`` if chain went all the way through, ``False`` if not
        """

        ktr = Kentauros(LOGPREFIX)

        def print_abort_msg():
            """This function prints a standard abort message."""
            ktr.log("Action aborted.", 2)

        verified = VerifyAction(self.kpkg, self.force).execute()
        if not verified:
            print_abort_msg()
            return False

        get = GetAction(self.kpkg, self.force).execute()
        if not get:
            ktr.log("Sources not downloaded.", 2)

        update = UpdateAction(self.kpkg, self.force).execute()
        if not update:
            ktr.log("Sources not updated.", 2)

        if not (get or update or self.force):
            ktr.log("No source changes were detected, aborting action.", 2)
            return False

        ExportAction(self.kpkg, self.force).execute()

        success = ConstructAction(self.kpkg, self.force).execute()
        if not success:
            print_abort_msg()
            return False

        success = BuildAction(self.kpkg, self.force).execute()
        if not success:
            print_abort_msg()
            return False

        UploadAction(self.kpkg, self.force).execute()

        return True
