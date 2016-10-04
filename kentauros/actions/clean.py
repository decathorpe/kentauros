"""
This submodule contains the :py:class:`CleanAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.abstract import Action


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

        self.kpkg.get_module("source").clean()
        return True
