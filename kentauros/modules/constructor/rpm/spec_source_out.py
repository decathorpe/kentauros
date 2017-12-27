"""
This sub-module contains the functions that generate the necessary "Source0:" tags for the .spec
file.
"""


import os

from ....package import KtrPackage

from .spec_common import format_tag_line


def spec_source_bzr(package: KtrPackage) -> str:
    """
    This function returns the Source tag for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a Source tag will be generated for

    Returns:
        str:                Source tag with comments
    """

    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", "%{name}-%{version}.tar.gz")

    return src_str


def spec_source_git(package: KtrPackage) -> str:
    """
    This function returns the Source string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a Source tag will be generated for

    Returns:
        str:                Source tag with comments
    """

    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", "%{name}-%{version}.tar.gz")

    return src_str


def spec_source_local(package: KtrPackage) -> str:
    """
    This function returns the Source string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a Source tag will be generated for

    Returns:
        str:                    Source tag in the format `Source0: $VERSION`
    """

    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", os.path.basename(package.conf.get("local", "orig")))
    return src_str


def spec_source_url(package: KtrPackage) -> str:
    """
    This function returns the Source string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a Source tag will be generated for

    Returns:
        str:                Source tag in the format `Source0: $URL`
    """

    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", package.conf.get("url", "orig"))
    return src_str


SPEC_SOURCE_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec Source tag string
generator functions.
"""

SPEC_SOURCE_DICT["bzr"] = spec_source_bzr
SPEC_SOURCE_DICT["git"] = spec_source_git
SPEC_SOURCE_DICT["local"] = spec_source_local
SPEC_SOURCE_DICT["url"] = spec_source_url
