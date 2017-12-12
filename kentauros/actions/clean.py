"""
This submodule contains the :py:class:`CleanAction` class.
"""

import warnings

from ..definitions import ActionType
from ..instance import Kentauros
from ..logcollector import LogCollector
from ..modules.module import PkgModule
from ..result import KtrResult

from .abstract import Action


class CleanAction(Action):
    """
    This :py:class:`Action` subclass contains information for cleaning up the sources of the package
    specified at initialisation.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.CLEAN``
    """

    NAME = "Clean Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CLEAN

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        """
        This method cleans up the sources of to the package specified at initialisation. It executes
        the :py:meth:`Source.clean()` method of the :py:class:`Source` instance in the specified
        package.

        Returns:
            bool:           always ``True`` at the moment
        """

        ktr = Kentauros()

        success = True
        logger = LogCollector(self.name())
        state = dict()

        ret = KtrResult(messages=logger, state=state)

        for module in self.kpkg.get_modules():
            assert isinstance(module, PkgModule)

            res: KtrResult = module.clean()
            ret.collect(res)

            if not res.success:
                logger.log("Module '" + str(module) + "' did not clean up successfully.")

            success = success and res.success

        if ktr.cli.get_remove():
            warnings.warn("Calling this method is dangerous!", DeprecationWarning)
            pkgid = ktr.state_delete(self.kpkg.get_conf_name())

            if pkgid is None:
                logger.log("Package not present in the database.")
            else:
                assert isinstance(pkgid, int)

                logger.log("Removed package " + self.kpkg.get_conf_name() + " from the database.")
                logger.log("Removed package had ID: " + str(pkgid))

        if success:
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return ret.submit(success)
