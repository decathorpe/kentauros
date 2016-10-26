"""
This sub-module contains the functions that generate the necessary version strings for the .spec
file, which depend on the type of source that is used.
"""


from kentauros.definitions import SourceType

from kentauros.modules.sources.bzr import BzrSource
from kentauros.modules.sources.git import GitSource
from kentauros.modules.sources.url import UrlSource
from kentauros.modules.sources.local import LocalSource


def spec_preamble_bzr(source: BzrSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from *bzr* repositories.
    This includes a definition of "rev" just now.

    Arguments:
        BzrSource source:   source repository the revision will be determined from

    Returns:
        str:                string containing the ``%defines rev $REV`` line
    """

    assert isinstance(source, BzrSource)
    rev_define = "%define rev " + source.rev() + "\n"
    return rev_define + "\n"


def spec_preamble_git(source: GitSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from *git* repositories. This
    includes a definition of "commit" and "date" just now. The value of "commit" here are the first
    8 characters of the corresponding git commit hash.

    Arguments:
        GitSource source:   source repository the commit hash and date will be determined from

    Returns:
        str:                string with the "%defines commit COMMIT" and "%defines date $DATE" lines
    """

    assert isinstance(source, GitSource)
    date_define = "%define date " + source.date() + "\n"
    commit_define = "%define commit " + source.commit()[0:8] + "\n"
    return date_define + commit_define + "\n"


def spec_preamble_url(source: UrlSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from tarballs specified by
    *url*.

    Arguments:
        UrlSource source:   source the ``%defines`` will be determined from

    Returns:
        str:                empty string
    """

    assert isinstance(source, UrlSource)
    return ""


def spec_preamble_local(source: LocalSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from tarballs specified by a
    *local path*.

    Arguments:
        LocalSource source:     source the ``%defines`` will be determined from

    Returns:
        str:                    empty string
    """

    assert isinstance(source, LocalSource)
    return ""


SPEC_PREAMBLE_DICT = dict()
"""This dictionary maps `SourceType` enum members to their respective RPM spec preamble generator
functions.
"""

SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.LOCAL] = spec_preamble_local
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url
