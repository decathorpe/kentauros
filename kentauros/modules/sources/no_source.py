"""
This sub-module only contains a dummy `NoSource` class which acts as a smart placeholder in case no
source module is defined in the package configuration file.
"""


import warnings

from kentauros.definitions import SourceType
from kentauros.modules.sources.abstract import Source


LOG_PREFIX = "ktr/sources/none"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""

ERROR_STRING = "kentauros is attempting to run an unsupported method on a NoSource object."


class NoSource(Source):
    """
    This Source subclass does nothing except be a smart placeholder for packages that don't define a
    source module in their package configuration.

    Arguments:
        Package package:    package instance this :py:class:`NoSource` belongs to
    """

    def __init__(self, package):
        super().__init__(package)

        self.stype = SourceType.NONE

    def __str__(self) -> str:
        return "placeholder Source for Package '" + self.spkg.get_conf_name() + "'"

    def verify(self) -> bool:
        warnings.warn(ERROR_STRING, Warning)
        return True

    def get_keep(self) -> bool:
        warnings.warn(ERROR_STRING, Warning)
        return True

    def get_orig(self) -> str:
        warnings.warn(ERROR_STRING, Warning)
        return ""

    def status(self) -> dict:
        warnings.warn(ERROR_STRING, Warning)
        return dict()

    def status_string(self) -> str:
        warnings.warn(ERROR_STRING, Warning)
        return ""

    def imports(self) -> dict:
        warnings.warn(ERROR_STRING, Warning)
        return dict()

    def formatver(self) -> str:
        return self.spkg.get_version()

    def get(self) -> bool:
        warnings.warn(ERROR_STRING, Warning)
        return True

    def update(self) -> bool:
        warnings.warn(ERROR_STRING, Warning)
        return True

    def export(self) -> bool:
        warnings.warn(ERROR_STRING, Warning)
        return True
