"""
This subpackage contains the :py:class:`Source` base class an :py:class:`BzrSource`,
:py:class:`GitSource`, :py:class:`LocalSource` and :py:class:`UrlSource` subclasses, which are used
for holding information about a package's sources and methods for manipulating them. Additionally,
this file contains a dictionary which maps :py:class:`SourceType` enums to their respective class
constructors.
"""

from ...context import KtrContext
from ...definitions import SourceType
from ...package import KtrPackage

from .abstract import Source
from .bzr import BzrSource
from .git import GitSource
from .url import UrlSource
from .local import LocalSource


def get_source(stype: SourceType, package: KtrPackage, context: KtrContext) -> Source:
    """
    This function constructs a `Source` from a `SourceType` enum member and a package.
    """

    source_dict = dict()

    source_dict[SourceType.BZR] = BzrSource
    source_dict[SourceType.GIT] = GitSource
    source_dict[SourceType.LOCAL] = LocalSource
    source_dict[SourceType.URL] = UrlSource

    return source_dict[stype](package, context)
