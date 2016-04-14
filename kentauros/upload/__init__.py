"""
This subpackage contains the :py:class:`Uploader` base class and
:py:class:`CoprUploader`, which is used for holding information about a
package's upload location or method (if defined in package configuration).
Additionally, this file contains a dictioary which maps :py:class:`UploaderType`
enums to their respective class constructors.
"""


from kentauros.definitions import UploaderType

from kentauros.upload.uploader import Uploader
from kentauros.upload.copr import CoprUploader


__all__ = ["copr", "uploader"]


UPLOADER_TYPE_DICT = dict()
""" This dictionary maps `UploaderType` enum members to their respective
`Uploader` subclass constructors.
"""

UPLOADER_TYPE_DICT[UploaderType.COPR] = CoprUploader
UPLOADER_TYPE_DICT[UploaderType.NONE] = Uploader

