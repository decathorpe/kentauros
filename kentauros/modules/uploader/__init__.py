"""
This subpackage contains the :py:class:`Uploader` base class and :py:class:`CoprUploader`, which is
used for holding information about a package's upload location or method (if defined in package
configuration). Additionally, this file contains a dictionary which maps :py:class:`UploaderType`
enums to their respective class constructors.
"""


from ...context import KtrContext
from ...package import KtrPackage

from .abstract import Uploader
from .copr import CoprUploader


def get_uploader(utype: str, package: KtrPackage, context: KtrContext) -> Uploader:
    """
    This function constructs an `Uploader` from an `UploaderType` enum member and a package.
    """
    uploader_dict = dict()

    uploader_dict["copr"] = CoprUploader

    return uploader_dict[utype](package, context)


__all__ = ["get_uploader"]
