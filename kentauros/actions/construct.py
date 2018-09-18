"""
This submodule contains the :py:class:`ConstructAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.logger import KtrLogger

from kentauros.actions.abstract import Action
from kentauros.actions.common import LOGPREFIX


class ConstructAction(Action):
    """
    This :py:class:`Action` subclass contains information for constructing the source package from
    sources and package specification for the package specified at initialisation.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.CONSTRUCT``
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CONSTRUCT

    def execute(self) -> bool:
        logger = KtrLogger(LOGPREFIX)

        constructor = self.kpkg.get_module("constructor")

        if constructor is None:
            logger.log("This package doesn't define a constructor module. Aborting.")
            return True

        success = constructor.execute()

        if success:
            self.update_status()
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return success