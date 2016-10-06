"""
This submodule contains the :py:class:`UploadAction` class.
"""


from kentauros.definitions import ActionType
from kentauros.logger import KtrLogger

from kentauros.actions.abstract import Action
from kentauros.actions.common import LOGPREFIX


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

        uploader = self.kpkg.get_module("uploader")

        if uploader is None:
            KtrLogger(LOGPREFIX).log("This package doesn't define an uploader module. Aborting.")
            return True

        success = uploader.execute()

        self.update_status()

        return success
