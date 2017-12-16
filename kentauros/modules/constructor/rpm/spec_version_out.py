"""
This sub-module contains the functions that generate the necessary "Version:" tags for the .spec
file.
"""


from ....definitions import SourceType

from ...sources.bzr import BzrSource
from ...sources.git import GitSource
from ...sources.url import UrlSource
from ...sources.local import LocalSource
from ...sources.no_source import NoSource


def spec_version_bzr(source: BzrSource) -> str:
    """
    This function returns the version string for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION+rev%{rev}`
    """

    assert isinstance(source, BzrSource)

    template: str = source.context.conf.get("main", "version_template_bzr")

    if "%{version}" in template:
        template = template.replace("%{version}", source.package.get_version())
    if "%{version_sep}" in template:
        template = template.replace("%{version_sep}", source.package.get_version_separator())

    return template


def spec_version_git(source: GitSource) -> str:
    """
    This function returns the version string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION+git%{date}.%{commit}`
    """

    assert isinstance(source, GitSource)

    template: str = source.context.conf.get("main", "version_template_git")

    if "%{version}" in template:
        template = template.replace("%{version}", source.package.get_version())
    if "%{version_sep}" in template:
        template = template.replace("%{version_sep}", source.package.get_version_separator())

    return template


def spec_version_local(source: LocalSource) -> str:
    """
    This function returns the version string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a version string will be generated for

    Returns:
        str:                    version string in the format `$VERSION`
    """

    assert isinstance(source, LocalSource)
    ver_str = source.package.get_version()
    return ver_str


def spec_version_url(source: UrlSource) -> str:
    """
    This function returns the version string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION`
    """

    assert isinstance(source, UrlSource)
    ver_str = source.package.get_version()
    return ver_str


def spec_version_nosource(source: NoSource) -> str:
    """
    This function returns the version string for packages built without sources.

    Arguments:
        NoSource source:    source a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION`
    """

    assert isinstance(source, NoSource)
    ver_str = source.package.get_version()
    return ver_str


SPEC_VERSION_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec version string
generator functions.
"""

SPEC_VERSION_DICT[SourceType.BZR] = spec_version_bzr
SPEC_VERSION_DICT[SourceType.GIT] = spec_version_git
SPEC_VERSION_DICT[SourceType.LOCAL] = spec_version_local
SPEC_VERSION_DICT[SourceType.NONE] = spec_version_nosource
SPEC_VERSION_DICT[SourceType.URL] = spec_version_url
