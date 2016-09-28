"""
This submodule contains the :py:class:`GetAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.act_abstract import Action


class GetAction(Action):
    """
    This `Action` subclass contains information for downloading or copying the package's source
    from the specified origin. Either a VCS repository will be cloned by the appropriate tool, or a
    tarball will be downloaded from URL, or a local copy will be made.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.GET`
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.GET

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.get()` method to execute the source download /
        copy, if possible / necessary.

        Returns:
            bool:           *True* when successful, *False* if action failed
        """

        return self.kpkg.source.get()
