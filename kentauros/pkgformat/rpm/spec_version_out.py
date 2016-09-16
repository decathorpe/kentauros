"""
This submodule contains the functions that generate the necessary "%defines" for the .spec file,
which are included as that file's preamble.
"""


from kentauros.definitions import SourceType

from kentauros.sources.src_bzr import BzrSource
from kentauros.sources.src_git import GitSource
from kentauros.sources.src_local import LocalSource
from kentauros.sources.src_url import UrlSource


def spec_version_bzr(source: BzrSource) -> str:
    """
    This function returns the version string for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format ``$VERSION~rev%{rev}``
    """

    assert isinstance(source, BzrSource)
    ver_str = source.spkg.conf.get("source", "version") + "~rev%{rev}"
    return ver_str


def spec_version_git(source: GitSource) -> str:
    """
    This function returns the version string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format ``$VERSION~git%{date}~%{rev}``
    """

    assert isinstance(source, GitSource)
    ver_str = source.spkg.conf.get("source", "version") + "~git%{date}~%{rev}"
    return ver_str


def spec_version_local(source: LocalSource) -> str:
    """
    This function returns the version string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a version string will be generated for

    Returns:
        str:                    version string in the format ``$VERSION``
    """

    assert isinstance(source, LocalSource)
    ver_str = source.spkg.conf.get("source", "version")
    return ver_str


def spec_version_url(source: UrlSource) -> str:
    """
    This function returns the version string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a version string will be generated for

    Returns:
        str:                version string in the format ``$VERSION``
    """

    assert isinstance(source, UrlSource)
    ver_str = source.spkg.conf.get("source", "version")
    return ver_str


SPEC_VERSION_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec version string
generator functions.
"""

SPEC_VERSION_DICT[SourceType.BZR] = spec_version_bzr
SPEC_VERSION_DICT[SourceType.GIT] = spec_version_git
SPEC_VERSION_DICT[SourceType.LOCAL] = spec_version_local
SPEC_VERSION_DICT[SourceType.URL] = spec_version_url
