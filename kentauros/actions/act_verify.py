"""
This submodule contains the :py:class:`VerifyAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.logger import KtrLogger

from kentauros.actions.act_abstract import Action
from kentauros.actions.act_common import LOGPREFIX


class VerifyAction(Action):
    """
    This `Action` subclass contains information for making sure the package's configuration file is
    valid and everything needed for actions is in place.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.VERIFY`
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.VERIFY

    def execute(self) -> bool:
        """
        This method executes a verification of the package configuration and checks if every file
        necessary for actions is present (and valid).

        Currently, this does no checking whatsoever.
        """

        if not self.kpkg.verify():
            KtrLogger(LOGPREFIX).log("Package configuration could not be verified.", 2)
            return False
        else:
            return True
