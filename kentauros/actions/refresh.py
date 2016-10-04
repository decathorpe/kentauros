"""
This submodule contains the :py:class:`RefreshAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.abstract import Action


class RefreshAction(Action):
    """
    This `Action` subclass contains information for refreshing the package's source. Sources will be
    cleaned up and re-downloaded as specified.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.REFRESH`
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.REFRESH

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.refresh()` method to execute a source refresh.
        This includes cleaning up the package's source directory and redownloading or copying
        sources from origin to destination.

        Returns:
            bool:           *True* when successful, *False* if sub-action fails
        """

        return self.kpkg.get_module("source").refresh()
