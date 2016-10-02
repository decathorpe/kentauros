"""
This submodule contains the :py:class:`StatusAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.abstract import Action


class StatusAction(Action):
    """
    This `Action` subclass contains information for displaying packages which are configured for
    use with kentauros. At the moment, this only includes printing a list of packages, which is done
    by default when kentauros is run. More status messages are plannned for the future.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.STATUS`
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.STATUS

    def execute(self) -> bool:
        """
        This method prints a pretty summary of a package's configuration values to the console.
        Currently, this does nothing whatsoever.
        """

        # TODO: output package configuration / status
        return True
