"""
This submodule contains the :py:class:`StatusAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.package import Package

from kentauros.actions.act_abstract import Action


class StatusAction(Action):
    """
    This `Action` subclass contains information for displaying packages which are configured for
    use with kentauros. At the moment, this only includes printing a list of packages, which is done
    by default when kentauros is run. More status messages are plannned for the future.

    Arguments:
        Package kpkg:       Package instance for which status will be printed
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.STATUS`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.STATUS

    def execute(self) -> bool:
        """
        This method prints a pretty summary of a package's configuration values to the console.
        Currently, this does nothing whatsoever.
        """

        # TODO: output package configuration / status
        return True
