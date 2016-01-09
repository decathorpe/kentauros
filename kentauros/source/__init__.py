"""
kentauros.source module
contains Source class and methods
Source class contains information about package upstream source and methods to
manipulate them.
"""

from kentauros.source.bzr import BzrSource
from kentauros.source.common import SourceType
from kentauros.source.git import GitSource
from kentauros.source.local import LocalSource
from kentauros.source.srpm import SrpmSource
from kentauros.source.url import UrlSource


SOURCE_TYPE_DICT = dict()
SOURCE_TYPE_DICT[SourceType.BZR] = BzrSource
SOURCE_TYPE_DICT[SourceType.GIT] = GitSource
SOURCE_TYPE_DICT[SourceType.LOCAL] = LocalSource
SOURCE_TYPE_DICT[SourceType.SRPM] = SrpmSource
SOURCE_TYPE_DICT[SourceType.URL] = UrlSource

