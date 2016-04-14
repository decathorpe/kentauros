"""
This subpackage contains the :py:class:`Source` base class and
:py:class:`BzrSource`, :py:class:`GitSource`, :py:class:`LocalSource` and
:py:class:`UrlSource` subclasses, which are used for holding information
about a package's sources and methods for manipulating them. Additionally, this
file contains a dictioary which maps :py:class:`SourceType` enums to their
respective class constructors.
"""


from kentauros.definitions import SourceType

from kentauros.source.source import Source

from kentauros.source.bzr import BzrSource
from kentauros.source.git import GitSource
from kentauros.source.local import LocalSource
from kentauros.source.url import UrlSource


__all__ = ["bzr", "git", "local", "source", "url"]


SOURCE_TYPE_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective
`Source` subclass constructors.
"""

SOURCE_TYPE_DICT[SourceType.BZR] = BzrSource
SOURCE_TYPE_DICT[SourceType.GIT] = GitSource
SOURCE_TYPE_DICT[SourceType.LOCAL] = LocalSource
SOURCE_TYPE_DICT[SourceType.NONE] = Source
SOURCE_TYPE_DICT[SourceType.URL] = UrlSource

