"""
This submodule contains the :py:class:`VerifyAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.package import Package

from kentauros.actions.act_abstract import Action
from kentauros.actions.act_common import LOGPREFIX


class VerifyAction(Action):
    """
    This `Action` subclass contains information for making sure the package's configuration file is
    valid and everything needed for actions is in place.

    Arguments:
        Package kpkg:       validation will be done for `package`
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.VERIFY`
    """

    def __init__(self, kpkg: Package):
        super().__init__(kpkg)
        self.atype = ActionType.VERIFY

    def execute(self) -> bool:
        """
        This method executes a verification of the package configuration and checks if every file
        necessary for actions is present (and valid).

        Currently, this does no checking whatsoever.
        """

        if not self.kpkg.verify():
            Kentauros(LOGPREFIX).log("Package configuration could not be verified.", 2)
            return False
        else:
            return True
