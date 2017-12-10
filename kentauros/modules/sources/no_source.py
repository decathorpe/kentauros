"""
This sub-module only contains a dummy `NoSource` class which acts as a smart placeholder in case no
source module is defined in the package configuration file.
"""


import warnings

from ...definitions import SourceType
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

    def __init__(self, package):
        super().__init__(package)

        self.stype = SourceType.NONE

    def __str__(self) -> str:
        return "placeholder Source for Package '" + self.spkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult.true()

    def get_keep(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult.true()

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

    def get(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult.true()

    def update(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult.true()

    def export(self) -> KtrResult:
        warnings.warn(ERROR_STRING, Warning)
        return KtrResult.true()
