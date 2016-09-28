"""
This submodule contains the :py:class:`CleanAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.act_abstract import Action


class CleanAction(Action):
    """
    This :py:class:`Action` subclass contains information for cleaning up the sources of the package
    specified at initialisation.

    Arguments:
        Package kpkg:       package that sources will be cleaned up for
        bool force:         currently without effect (common flag of actions)

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

        self.kpkg.source.clean()
        return True
