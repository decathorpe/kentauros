"""
This submodule contains the :py:class:`ExportAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.abstract import Action


class ExportAction(Action):
    """
    This `Action` subclass contains information for exporting the specified source from a VCS
    repository to a tarball (if necessary). It does not have any effect for local tarballs and
    tarballs specified by URL.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.EXPORT`
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.EXPORT

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.export()` method to execute the source export,
        if possible / necessary.

        Returns:
            bool:           *True* when successful, *False* if file exists
        """

        return self.kpkg.get_module("source").export()
