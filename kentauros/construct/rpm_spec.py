"""
# TODO: napoleon module docstring
kentauros.construct.rpm_spec
contains helper functions for building rpm source packages
"""


import io
import subprocess

from kentauros.definitions import SourceType
from kentauros.instance import Kentauros, log_command

from kentauros.source.source import Source


LOGPREFIX1 = "ktr/construct/rpm_spec: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class RPMSpecError(Exception):
    """
    # TODO: napoleon class docstring
    kentauros.construct.rpm_spec.RPMSpecError:
    exception for rpm spec errors
    """

    def __init__(self, value):
        super().__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


def spec_preamble_bzr(source: Source):
    """
    This function returns the "%defines" necessary for packages built from *bzr*
    repositories. This includes a definition of "rev" just now.

    Arguments:
        Source source: source repository the revision will be determined from

    Returns:
        str: string containing the ``%defines rev $REV`` line
    """

    assert isinstance(source, Source)
    rev_define = "%define rev " + source.rev() + "\n"
    return rev_define + "\n"


def spec_preamble_git(source: Source):
    """
    This function returns the "%defines" necessary for packages built from *git*
    repositories. This includes a definition of "rev" and "date" just now. The
    value of "rev" here are the first 8 characters of the corresponding git
    commit hash.

    Arguments:
        Source source: source repository the revision will be determined from

    Returns:
        str: string with the "%defines rev $REV" and "%defines date $DATE" lines
    """

    assert isinstance(source, Source)
    date_define = "%define date " + source.date() + "\n"
    rev_define = "%define rev " + source.rev()[0:8] + "\n"
    return date_define + rev_define + "\n"


def spec_preamble_url(source: Source):
    """
    This function returns the "%defines" necessary for packages built from
    tarballs specified by *url*.

    Arguments:
        Source source: source the ``%defines`` will be determined from

    Returns:
        str: empty string
    """

    assert isinstance(source, Source)
    return ""


SPEC_PREAMBLE_DICT = dict()
# TODO: napoleon variable docstring
SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url


def spec_version_bzr(source: Source):
    """
    This function returns the version string for packages built from *bzr*
    repositories.

    Arguments:
        Source source: source repository a version string will be generated for

    Returns:
        str: version string in the format ``$VERSION~rev%{rev}``
    """

    assert isinstance(source, Source)
    ver_str = source.conf.get("source", "version") + "~rev%{rev}"
    return ver_str


def spec_version_git(source: Source):
    """
    This function returns the version string for packages built from *git*
    repositories.

    Arguments:
        Source source:  source repository a version string will be generated for

    Returns:
        str: version string in the format ``$VERSION~git%{date}~%{rev}``
    """

    assert isinstance(source, Source)
    ver_str = source.conf.get("source", "version") + "~git%{date}~%{rev}"
    return ver_str


def spec_version_url(source: Source):
    """
    This function returns the version string for packages built from tarballs
    specified by *url*.

    Arguments:
        Source source:  source a version string will be generated for

    Returns:
        str: version string in the format ``$VERSION``
    """

    assert isinstance(source, Source)
    ver_str = source.conf.get("source", "version")
    return ver_str


SPEC_VERSION_DICT = dict()
# TODO: napoleon variable docstring
SPEC_VERSION_DICT[SourceType.BZR] = spec_version_bzr
SPEC_VERSION_DICT[SourceType.GIT] = spec_version_git
SPEC_VERSION_DICT[SourceType.URL] = spec_version_url


def spec_version_read(file_obj: io.IOBase):
    """
    This function reads and parses an RPM spec file for its "Version" tag.

    Arguments:
        io.IOBase file_obj: file object corresponding the the RPM spec file

    Returns:
        str: version string found on the line containing the "Version:" tag
    """

    assert isinstance(file_obj, io.IOBase)

    file_obj.seek(0)
    for line in file_obj:
        if line[0:8] == "Version:":
            file_obj.seek(0)
            return line.replace("Version:", "").lstrip(" ").rstrip("\n")

    file_obj.seek(0)
    raise RPMSpecError("No Version tag was found in the file.")


def spec_release_read(file_obj: io.IOBase):
    """
    This function reads and parses an RPM spec file for its "Release:" tag.

    Arguments:
        io.IOBase file_obj: file object corresponding the the RPM spec file

    Returns:
        str: release string found on the line containing the "Release:" tag
    """

    assert isinstance(file_obj, io.IOBase)

    file_obj.seek(0)
    for line in file_obj:
        if line[0:8] == "Release:":
            file_obj.seek(0)
            return line.replace("Release:", "").lstrip(" ").rstrip("\n")

    file_obj.seek(0)
    raise RPMSpecError("No Release tag was found in the file.")


def if_version(line: str):
    """
    This function returns ``True`` if the line contains the "Version:" tag and
    ``False`` if not.

    Arguments:
        str line: string to be processed

    Returns:
        bool: "Version:" tag present or not
    """

    return line[0:8] == "Version:"


def if_release(line: str):
    """
    This function returns ``True`` if the line contains the "Release:" tag and
    ``False`` if not.

    Arguments:
        str line: string to be processed

    Returns:
        bool: "Release:" tag present or not
    """

    return line[0:8] == "Release:"


def bump_release(relstr_old: str, reset: bool=False, change: bool=False):
    """
    This function takes an old release string, processes it and returns a new
    release string. By default, this does nothing to the string, because the
    release string will be bumped by :py:func:`spec_bump` anyway.

    Arguments:
        str relstr_old: old release string
        bool reset:  switch to enable release reset to "0whatever" (for example
                     after version changes)
        bool change: switch to enable changes (incrementing first digit by 1)
    """

    release_inum = int(relstr_old[0])
    release_rest = relstr_old[1:]

    if not change and not reset:
        return relstr_old
    if not reset and change:
        return str(release_inum + 1) + release_rest
    if reset:
        return str(0) + release_rest


def spec_bump(specfile: str, comment: str=None):
    """
    This function calls ``rpmdev-bumpspec`` with the specified arguments to
    bump the release number and create a changelog entry with a given comment.

    Arguments:
        str specfile: absolute path of RPM spec file to process
        str comment:  comment to be added to the changelog entry
    """

    ktr = Kentauros()

    if comment is None:
        comment = "automatic build by kentauros"

    # construct rpmdev-bumpspec command
    cmd = ["rpmdev-bumpspec"]

    # add --verbose or --quiet depending on settings
    if (ktr.verby == 0) or ktr.debug:
        cmd.append("--verbose")

    cmd.append(specfile)

    cmd.append('--comment=' + comment)

    log_command(LOGPREFIX1, "rpmdev-bumpspec", cmd, 1)
    subprocess.call(cmd)

    # TODO: error handling

