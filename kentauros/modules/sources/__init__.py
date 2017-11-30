"""
This subpackage contains the :py:class:`Source` base class an :py:class:`BzrSource`,
:py:class:`GitSource`, :py:class:`LocalSource` and :py:class:`UrlSource` subclasses, which are used
for holding information about a package's sources and methods for manipulating them. Additionally,
this file contains a dictionary which maps :py:class:`SourceType` enums to their respective class
constructors.
"""


from kentauros.modules.sources.abstract import Source
from kentauros.modules.sources.bzr import BzrSource
from kentauros.modules.sources.git import GitSource
from kentauros.modules.sources.url import UrlSource
from kentauros.modules.sources.local import LocalSource

from kentauros.definitions import SourceType


def get_source(stype: SourceType, package) -> Source:
    """
    This function constructs a `Source` from a `SourceType` enum member and a package.
    """

    source_dict = dict()

    source_dict[SourceType.BZR] = BzrSource
    source_dict[SourceType.GIT] = GitSource
    source_dict[SourceType.LOCAL] = LocalSource
    source_dict[SourceType.URL] = UrlSource

    return source_dict[stype](package)
