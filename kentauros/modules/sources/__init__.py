"""
This subpackage contains the :py:class:`Source` base class an :py:class:`BzrSource`,
:py:class:`GitSource`, :py:class:`LocalSource` and :py:class:`UrlSource` subclasses, which are used
for holding information about a package's sources and methods for manipulating them. Additionally,
this file contains a dictioary which maps :py:class:`SourceType` enums to their respective class
constructors.
"""


from kentauros.modules.sources.src_bzr import BzrSource
from kentauros.modules.sources.src_git import GitSource
from kentauros.modules.sources.src_url import UrlSource
from kentauros.modules.sources.src_local import LocalSource

from kentauros.definitions import SourceType


SOURCE_TYPE_DICT = dict()
""" This dictionary maps :py:class:`SourceType` enum members to their respective :py:class:`Source`
subclass constructors.
"""

SOURCE_TYPE_DICT[SourceType.BZR] = BzrSource
SOURCE_TYPE_DICT[SourceType.GIT] = GitSource
SOURCE_TYPE_DICT[SourceType.LOCAL] = LocalSource
SOURCE_TYPE_DICT[SourceType.URL] = UrlSource
