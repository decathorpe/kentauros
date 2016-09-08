"""
This submodule contains the :py:class:`GetAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.package import Package

from kentauros.actions.act_abstract import Action


class GetAction(Action):
    """
    This `Action` subclass contains information for downloading or copying the package's source
    from the specified origin. Either a VCS repository will be cloned by the appropriate tool, or a
    tarball will be downloaded from URL, or a local copy will be made.

    Arguments:
        Package kpkg:       package source getting will be attempted for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.GET`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.GET

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.get()` method to execute the source download /
        copy, if possible / necessary.

        Returns:
            bool:           *True* when successful, *False* if action failed
        """

        return self.kpkg.source.get()
