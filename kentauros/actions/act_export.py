"""
This submodule contains the :py:class:`ExportAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.package import Package

from kentauros.actions.act_abstract import Action


class ExportAction(Action):
    """
    This `Action` subclass contains information for exporting the specified source from a VCS
    repository to a tarball (if necessary). It does not have any effect for local tarballs and
    tarballs specified by URL.

    Arguments:
        Package kpkg:       Package instance source export will be attempted for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.EXPORT`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.EXPORT

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.export()` method to execute the source export,
        if possible / necessary.

        Returns:
            bool:           *True* when successful, *False* if file exists
        """

        return self.kpkg.source.export()
