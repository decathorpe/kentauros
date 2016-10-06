"""
This submodule contains the :py:class:`BuildAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.logger import KtrLogger

from kentauros.actions.abstract import Action
from kentauros.actions.common import LOGPREFIX


class BuildAction(Action):
    """
    This :py:class:`Action` subclass contains information for executing a local build of the package
    specified at initialisation.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.BUILD``
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.BUILD

    def execute(self) -> bool:
        builder = self.kpkg.get_module("builder")

        if builder is None:
            KtrLogger(LOGPREFIX).log("This package doesn't define a builder module. Aborting.")
            return True

        success = builder.execute()

        self.update_status()

        return success
