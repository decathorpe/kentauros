"""
This submodule contains the :py:class:`CleanAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.actions.abstract import Action
from kentauros.actions.common import LOGPREFIX


class CleanAction(Action):
    """
    This :py:class:`Action` subclass contains information for cleaning up the sources of the package
    specified at initialisation.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.CLEAN``
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CLEAN

    def execute(self) -> bool:
        """
        This method cleans up the sources of to the package specified at initialisation. It executes
        the :py:meth:`Source.clean()` method of the :py:class:`Source` instance in the specified
        package.

        Returns:
            bool:           always ``True`` at the moment
        """

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        success = True

        for module in self.kpkg.get_modules():
            cleanup = module.clean()

            if not cleanup:
                logger.log("Module '" + str(module) + "' did not clean up successfully.")

            success = success and cleanup

        if ktr.cli.get_remove():
            pkgid = ktr.state_delete(self.kpkg.get_conf_name())

            if pkgid is None:
                logger.log("Package not present in the database.")
            else:
                assert isinstance(pkgid, int)

                logger.log("Removed package " + self.kpkg.get_conf_name() + " from the database.")
                logger.log("Removed package had ID: " + str(pkgid), 0)

        if success:
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return success
