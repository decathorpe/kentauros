"""
This submodule contains the :py:class:`VerifyAction` class.
"""


from kentauros.definitions import ActionType
from kentauros.actions.abstract import Action


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
        necessary for actions is present (and valid). The real checks are done during package
        initialisation.
        """

        return True
