"""
This sub-module contains the functions that generate the necessary version strings for the .spec
file, which depend on the type of source that is used.
"""


from ....definitions import SourceType
from ....result import KtrResult

from ...sources.bzr import BzrSource
from ...sources.git import GitSource
from ...sources.url import UrlSource
from ...sources.local import LocalSource
from ...sources.no_source import NoSource


def spec_preamble_bzr(source: BzrSource) -> KtrResult:
    """
    This function returns the "%global" necessary for packages built from *bzr* repositories.
    This includes a definition of "rev" just now.

    Arguments:
        BzrSource source:   source repository the revision will be determined from

    Returns:
        str:                string containing the `%global rev $REV` line
    """

    assert isinstance(source, BzrSource)

    ret = KtrResult()

    rev = source.rev()
    date = source.date()
    time = source.time()

    if not rev.success:
        ret.messages.log("Bzr revision could not be determined correctly.")
        return ret.submit(False)

    if not date.success:
        ret.messages.log("Bzr revision date could not be determined correctly.")
        return ret.submit(False)

    if not time.success:
        ret.messages.log("Bzr revision time could not be determined correctly.")
        return ret.submit(False)

    rev_define = "%global revision " + rev.value + "\n"
    date_define = "%global date " + date.value + "\n"
    time_define = "%global time " + time.value + "\n"

    ret.value = rev_define + date_define + time_define + "\n"
    ret.klass = str

    ret.submit(True)


def spec_preamble_git(source: GitSource) -> KtrResult:
    """
    This function returns the "%globals" necessary for packages built from *git* repositories. This
    includes a definition of "commit" and "date" just now. The value of "commit" here are the first
    8 characters of the corresponding git commit hash.

    Arguments:
        GitSource source:   source repository the commit hash and date will be determined from

    Returns:
        str:                string with the `%global commit COMMIT` and `%global date $DATE` lines
    """

    assert isinstance(source, GitSource)

    ret = KtrResult()

    commit = source.commit()
    date = source.date()
    time = source.time()

    if not commit.success:
        ret.messages.log("Bzr revision could not be determined correctly.")
        return ret.submit(False)

    if not date.success:
        ret.messages.log("Bzr revision date could not be determined correctly.")
        return ret.submit(False)

    if not time.success:
        ret.messages.log("Bzr revision time could not be determined correctly.")
        return ret.submit(False)

    commit_define = "%global commit " + commit.value + "\n"
    shortcommit_define = "%global shortcommit %(c=%{commit}; echo ${c:0:7})" + "\n"
    date_define = "%global date " + date.value + "\n"
    time_define = "%global time " + time.value + "\n"

    ret.value = commit_define + shortcommit_define + date_define + time_define + "\n"
    ret.klass = str

    return ret.submit(True)


def spec_preamble_url(source: UrlSource) -> KtrResult:
    """
    This function returns the "%global" necessary for packages built from tarballs specified by
    *url*.

    Arguments:
        UrlSource source:   source the `%global` will be determined from

    Returns:
        str:                empty string
    """

    assert isinstance(source, UrlSource)
    return KtrResult(True, "", str)


def spec_preamble_local(source: LocalSource) -> KtrResult:
    """
    This function returns the "%global" necessary for packages built from tarballs specified by a
    *local path*.

    Arguments:
        LocalSource source:     source the `%global` will be determined from

    Returns:
        str:                    empty string
    """

    assert isinstance(source, LocalSource)
    return KtrResult(True, "", str)


def spec_preamble_nosource(source: NoSource) -> KtrResult:
    """
    This function returns an empty string.

    Arguments:
        NoSource source:    source the  `%global` will be determined from

    Returns:
        str:                empty string
    """

    assert isinstance(source, NoSource)
    return KtrResult(True, "", str)


SPEC_PREAMBLE_DICT = dict()
"""This dictionary maps `SourceType` enum members to their respective RPM spec preamble generator
functions.
"""

SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.LOCAL] = spec_preamble_local
SPEC_PREAMBLE_DICT[SourceType.NONE] = spec_preamble_nosource
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url
