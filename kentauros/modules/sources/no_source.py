"""
This sub-module only contains a dummy `NoSource` class which acts as a smart placeholder in case no
source module is defined in the package configuration file.
"""


import warnings

from ...context import KtrContext
from ...definitions import SourceType
from ...package import KtrPackage
from ...result import KtrResult

from .abstract import Source


ERROR_STRING = "kentauros is attempting to run an unsupported method on a NoSource object."


class NoSource(Source):
    """
    This Source subclass does nothing except be a smart placeholder for packages that don't define a
    source module in their package configuration.

    Arguments:
        Package package:    package instance this :py:class:`NoSource` belongs to
    """

    NAME = "Dummy Source"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.stype = SourceType.NONE

    def __str__(self) -> str:
        return "placeholder Source for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)

    def get_keep(self) -> bool:
        warnings.warn(ERROR_STRING, Warning)
        return True

    def get_orig(self) -> str:
        warnings.warn(ERROR_STRING, Warning)
        return ""

    def status(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)

    def imports(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)

    def formatver(self) -> KtrResult:
        return KtrResult(True, self.package.get_version())

    def get(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)

    def update(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)

    def export(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult(True)
