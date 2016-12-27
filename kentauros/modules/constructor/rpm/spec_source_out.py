"""
This sub-module contains the functions that generate the necessary "Source0:" tags for the .spec
file.
"""


import os
import warnings

from kentauros.definitions import SourceType

from kentauros.modules.sources.bzr import BzrSource
from kentauros.modules.sources.git import GitSource
from kentauros.modules.sources.url import UrlSource
from kentauros.modules.sources.local import LocalSource
from kentauros.modules.sources.no_source import NoSource

from kentauros.modules.constructor.rpm.spec_common import format_tag_line


def spec_source_bzr(source: BzrSource) -> str:
    """
    This function returns the Source tag for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a Source tag will be generated for

    Returns:
        str:                Source tag with comments
    """

    assert isinstance(source, BzrSource)

    src_str = ("# The tarball is generated from a checkout of the specified branch and\n" +
               "# by executing 'bzr export' and has the usual format\n" +
               "# ('%{name}-%{version}.tar.gz'), where %{version} contains the upstream\n" +
               "# version number with a '+bzr%{rev}' suffix specifying the bzr revision.\n" +
               format_tag_line("Source0", "%{name}-%{version}.tar.gz"))

    return src_str


def spec_source_git(source: GitSource) -> str:
    """
    This function returns the Source string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a Source tag will be generated for

    Returns:
        str:                Source tag with comments
    """

    assert isinstance(source, GitSource)

    src_str = ("# The tarball is generated from a clone of the specified branch and\n" +
               "# by executing 'git archive' and has the usual format\n" +
               "# ('%{name}-%{version}.tar.gz'), where %{version} contains the upstream\n" +
               "# version number with a '+git%{commit}.%{date}' suffix specifying the git\n"
               "# commit hash (8 characters) and the commit date and time (UTC).\n" +
               format_tag_line("Source0", "%{name}-%{version}.tar.gz"))

    return src_str


def spec_source_local(source: LocalSource) -> str:
    """
    This function returns the Source string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a Source tag will be generated for

    Returns:
        str:                    Source tag in the format `Source0: $VERSION`
    """

    assert isinstance(source, LocalSource)

    src_str = format_tag_line("Source0", os.path.basename(source.spkg.conf.get("local", "orig")))
    return src_str


def spec_source_url(source: UrlSource) -> str:
    """
    This function returns the Source string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a Source tag will be generated for

    Returns:
        str:                Source tag in the format `Source0: $URL`
    """

    assert isinstance(source, UrlSource)

    src_str = format_tag_line("Source0", source.spkg.conf.get("url", "orig"))
    return src_str


def spec_source_nosource(source: NoSource) -> str:
    """
    This function returns an empty string, as it should never be called.

    Arguments:
        NoSource source:    source the  `%defines` will be determined from

    Returns:
        str:                empty string
    """

    warnings.warn("This function should never be called.", Warning)
    assert isinstance(source, NoSource)
    return ""


SPEC_SOURCE_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec Source tag string
generator functions.
"""

SPEC_SOURCE_DICT[SourceType.BZR] = spec_source_bzr
SPEC_SOURCE_DICT[SourceType.GIT] = spec_source_git
SPEC_SOURCE_DICT[SourceType.LOCAL] = spec_source_local
SPEC_SOURCE_DICT[SourceType.NONE] = spec_source_nosource
SPEC_SOURCE_DICT[SourceType.URL] = spec_source_url
