"""
This sub-module contains the functions that generate the necessary "Version:" tags for the .spec
file.
"""

from ....context import KtrContext
from ....package import KtrPackage


def spec_version_bzr(package: KtrPackage, context: KtrContext) -> str:
    """
    This function returns the version string for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION+rev%{rev}`
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    template: str = context.conf.get("main", "version_template_bzr")

    if "%{version}" in template:
        template = template.replace("%{version}", package.get_version())
    if "%{version_sep}" in template:
        template = template.replace("%{version_sep}", package.get_version_separator())

    return template


def spec_version_git(package: KtrPackage, context: KtrContext) -> str:
    """
    This function returns the version string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION+git%{date}.%{commit}`
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    template: str = context.conf.get("main", "version_template_git")

    if "%{version}" in template:
        template = template.replace("%{version}", package.get_version())
    if "%{version_sep}" in template:
        template = template.replace("%{version_sep}", package.get_version_separator())

    return template


def spec_version_local(package: KtrPackage, context: KtrContext) -> str:
    """
    This function returns the version string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a version string will be generated for

    Returns:
        str:                    version string in the format `$VERSION`
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    ver_str = package.get_version()
    return ver_str


def spec_version_url(package: KtrPackage, context: KtrContext) -> str:
    """
    This function returns the version string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a version string will be generated for

    Returns:
        str:                version string in the format `$VERSION`
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    ver_str = package.get_version()
    return ver_str


SPEC_VERSION_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec version string
generator functions.
"""

SPEC_VERSION_DICT["bzr"] = spec_version_bzr
SPEC_VERSION_DICT["git"] = spec_version_git
SPEC_VERSION_DICT["local"] = spec_version_local
SPEC_VERSION_DICT["url"] = spec_version_url
