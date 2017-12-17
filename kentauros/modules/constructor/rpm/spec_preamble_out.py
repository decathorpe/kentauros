"""
This sub-module contains the functions that generate the necessary version strings for the .spec
file, which depend on the type of source that is used.
"""

from ....context import KtrContext
from ....definitions import SourceType
from ....package import KtrPackage
from ....result import KtrResult


def spec_preamble_bzr(package: KtrPackage, context: KtrContext) -> KtrResult:
    """
    This function returns the "%global" necessary for packages built from *bzr* repositories.
    This includes a definition of "rev" just now.

    Arguments:
        BzrSource source:   source repository the revision will be determined from

    Returns:
        str:                string containing the `%global rev $REV` line
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    ret = KtrResult()
    state = context.state.read(package.conf_name)

    rev: str = state["bzr_last_rev"]
    dt_string: str = state["bzr_last_date"]
    dt = dt_string.split(" ")

    date = dt[0]
    time = dt[1]

    rev_define = "%global revision " + rev + "\n"
    date_define = "%global date " + date + "\n"
    time_define = "%global time " + time + "\n"

    ret.value = rev_define + date_define + time_define + "\n"
    return ret.submit(True)


def spec_preamble_git(package: KtrPackage, context: KtrContext) -> KtrResult:
    """
    This function returns the "%globals" necessary for packages built from *git* repositories. This
    includes a definition of "commit" and "date" just now. The value of "commit" here are the first
    8 characters of the corresponding git commit hash.

    Arguments:
        GitSource source:   source repository the commit hash and date will be determined from

    Returns:
        str:                string with the `%global commit COMMIT` and `%global date $DATE` lines
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    ret = KtrResult()
    state = context.state.read(package.conf_name)

    commit: str = state["git_last_commit"]
    dt_string: str = state["git_last_date"]
    dt = dt_string.split(" ")

    date = dt[0]
    time = dt[1]

    commit_define = "%global commit " + commit + "\n"
    shortcommit_define = "%global shortcommit %(c=%{commit}; echo ${c:0:7})" + "\n"
    date_define = "%global date " + date + "\n"
    time_define = "%global time " + time + "\n"

    ret.value = commit_define + shortcommit_define + date_define + time_define + "\n"
    return ret.submit(True)


def spec_preamble_url(package: KtrPackage, context: KtrContext) -> KtrResult:
    """
    This function returns the "%global" necessary for packages built from tarballs specified by
    *url*.

    Arguments:
        UrlSource source:   source the `%global` will be determined from

    Returns:
        str:                empty string
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    return KtrResult(True, "")


def spec_preamble_local(package: KtrPackage, context: KtrContext) -> KtrResult:
    """
    This function returns the "%global" necessary for packages built from tarballs specified by a
    *local path*.

    Arguments:
        LocalSource source:     source the `%global` will be determined from

    Returns:
        str:                    empty string
    """

    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    return KtrResult(True, "")


SPEC_PREAMBLE_DICT = dict()
"""This dictionary maps `SourceType` enum members to their respective RPM spec preamble generator
functions.
"""

SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.LOCAL] = spec_preamble_local
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url
