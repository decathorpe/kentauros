"""
This submodule contains the functions that generate the necessary version strings for the .spec
file, which depend on the type of source that is used.
"""


from kentauros.definitions import SourceType

from kentauros.sources.src_bzr import BzrSource
from kentauros.sources.src_git import GitSource
from kentauros.sources.src_local import LocalSource
from kentauros.sources.src_url import UrlSource


def spec_preamble_bzr(source: BzrSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from *bzr*
    repositories. This includes a definition of "rev" just now.

    Arguments:
        BzrSource source: source repository the revision will be determined from

    Returns:
        str: string containing the ``%defines rev $REV`` line
    """

    assert isinstance(source, BzrSource)
    rev_define = "%define rev " + source.rev() + "\n"
    return rev_define + "\n"


def spec_preamble_git(source: GitSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from *git*
    repositories. This includes a definition of "rev" and "date" just now. The
    value of "rev" here are the first 8 characters of the corresponding git
    commit hash.

    Arguments:
        GitSource source: source repository the revision will be determined from

    Returns:
        str: string with the "%defines rev $REV" and "%defines date $DATE" lines
    """

    assert isinstance(source, GitSource)
    date_define = "%define date " + source.date() + "\n"
    rev_define = "%define rev " + source.rev()[0:8] + "\n"
    return date_define + rev_define + "\n"


def spec_preamble_url(source: UrlSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from
    tarballs specified by *url*.

    Arguments:
        UrlSource source: source the ``%defines`` will be determined from

    Returns:
        str: empty string
    """

    assert isinstance(source, UrlSource)
    return ""


def spec_preamble_local(source: LocalSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from
    tarballs specified by a *local path*.

    Arguments:
        LocalSource source: source the ``%defines`` will be determined from

    Returns:
        str: empty string
    """

    assert isinstance(source, LocalSource)
    return ""


SPEC_PREAMBLE_DICT = dict()
"""This dictionary maps `SourceType` enum members to their respective
RPM spec preamble generator functions.
"""

SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.LOCAL] = spec_preamble_local
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url
