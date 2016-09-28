"""
This submodule contains the :py:class:`UploadAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.actions.act_abstract import Action


class UploadAction(Action):
    """
    This `Action` subclass contains information for uploading the buildable source package to a
    cloud service (or similar) as specified in the package configuration.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.UPLOAD`
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.UPLOAD

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Uploader.upload()` method to execute the source upload,
        if possible - this only has effect for packages with a valid uploader specified in the
        package configuration file.

        Returns:
            bool:           always *True*, future error checking still missing
        """

        # TODO: error handling
        self.kpkg.uploader.upload()
        return True
