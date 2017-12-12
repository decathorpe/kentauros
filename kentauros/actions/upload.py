"""
This submodule contains the :py:class:`UploadAction` class.
"""


from ..definitions import ActionType
from ..logcollector import LogCollector
from ..result import KtrResult
from ..modules.module import PkgModule

from .abstract import Action


class UploadAction(Action):
    """
    This `Action` subclass contains information for uploading the buildable source package to a
    cloud service (or similar) as specified in the package configuration.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.UPLOAD`
    """

    NAME = "Upload Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.UPLOAD

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        """
        This method executes the :py:meth:`Uploader.upload()` method to execute the source upload,
        if possible - this only has effect for packages with a valid uploader specified in the
        package configuration file.

        Returns:
            bool:           always *True*, future error checking still missing
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        uploader: PkgModule = self.kpkg.get_module("uploader")

        if uploader is None:
            logger.log("This package doesn't define an uploader module. Aborting.")
            return ret.submit(True)

        res: KtrResult = uploader.execute()
        ret.collect(res)

        if res.success:
            logger.log(self.kpkg.get_conf_name() + ": Success!")
        else:
            logger.log(self.kpkg.get_conf_name() + ": Not successful.")

        return ret.submit(res.success)
