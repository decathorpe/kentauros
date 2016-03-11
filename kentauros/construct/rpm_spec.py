"""
kentauros.construct.rpm_spec
contains helper functions for building rpm source packages
"""

import io
import subprocess

from kentauros.definitions import SourceType
from kentauros.init import get_debug, get_verby, log_command
from kentauros.source.common import Source


LOGPREFIX1 = "ktr/construct/rpm_spec: "


class RPMSpecError(Exception):
    """
    kentauros.construct.rpm_spec.RPMSpecError:
    exception for rpm spec errors
    """
    def __init__(self, value):
        super().__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


def spec_preamble_bzr(source):
    """
    kentauros.construct.rpm_spec.spec_preamble_bzr():
    returns rpm spec %defines lines formatted nicely for bzr sources
    """
    assert isinstance(source, Source)
    rev_define = "%define rev " + source.rev() + "\n"
    return rev_define + "\n"

def spec_preamble_git(source):
    """
    kentauros.construct.rpm_spec.spec_preamble_git():
    returns rpm spec %defines lines formatted nicely for git sources
    """
    assert isinstance(source, Source)
    date_define = "%define date " + source.date() + "\n"
    rev_define = "%define rev " + source.rev()[0:8] + "\n"
    return date_define + rev_define + "\n"

def spec_preamble_url(source):
    """
    kentauros.construct.rpm_spec.spec_preamble_url():
    returns rpm spec %defines lines formatted nicely for url sources
    """
    assert isinstance(source, Source)
    return ""


SPEC_PREAMBLE_DICT = dict()
SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url


def spec_version_bzr(source):
    """
    kentauros.construct.rpm_spec.spec_version_bzr():
    returns rpm spec "Version:" tagline formatted nicely for bzr sources
    """
    assert isinstance(source, Source)
    ver_str = source.conf.get("source", "version") + "~rev%{rev}"
    return ver_str

def spec_version_git(source):
    """
    kentauros.construct.rpm_spec.spec_version_git():
    returns rpm spec "Version:" tagline formatted nicely for git sources
    """
    assert isinstance(source, Source)
    ver_str = source.conf.get("source", "version") + "~git%{date}~%{rev}"
    return ver_str

def spec_version_url(source):
    """
    kentauros.construct.rpm_spec.spec_version_url():
    returns rpm spec "Version:" tagline formatted nicely for url sources
    """
    assert isinstance(source, Source)
    ver_str = source.conf.get("source", "version")
    return ver_str


SPEC_VERSION_DICT = dict()
SPEC_VERSION_DICT[SourceType.BZR] = spec_version_bzr
SPEC_VERSION_DICT[SourceType.GIT] = spec_version_git
SPEC_VERSION_DICT[SourceType.URL] = spec_version_url


def spec_version_read(file_obj):
    """
    kentauros.construct.rpm_spec.spec_version_read():
    returns version string found on rpm spec "Version:" tagline
    """
    assert isinstance(file_obj, io.IOBase)

    file_obj.seek(0)
    for line in file_obj:
        if line[0:8] == "Version:":
            file_obj.seek(0)
            return line.replace("Version:", "").lstrip(" ").rstrip("\n")

    file_obj.seek(0)
    raise RPMSpecError("No Version tag was found in the file.")


def spec_release_read(file_obj):
    """
    kentauros.construct.rpm_spec.spec_release_read():
    returns release string found on rpm spec "Release:" tagline
    """
    assert isinstance(file_obj, io.IOBase)

    file_obj.seek(0)
    for line in file_obj:
        if line[0:8] == "Release:":
            file_obj.seek(0)
            return line.replace("Release:", "").lstrip(" ").rstrip("\n")

    file_obj.seek(0)
    raise RPMSpecError("No Release tag was found in the file.")


def if_version(line):
    """
    kentauros.construct.rpm_spec.if_version()
    function returns version string if "Version: " is found on spec file line
    """
    return line[0:8] == "Version:"


def if_release(line):
    """
    kentauros.construct.rpm_spec.if_release()
    function returns release string if "Release: " is found on spec file line
    """
    return line[0:8] == "Release:"


def bump_release(relstr_old, reset=False):
    """
    kentauros.construct.rpm_spec.bump_release()
    returns release string bumped by 1 (hopefully intelligently)
    """
    rnum = int(relstr_old[0])
    rest = relstr_old[1:]

    if not reset:
        return str(rnum + 1) + rest
    else:
        return str(0) + rest


def spec_bump(specfile, comment=None):
    """
    kentauros.construct.rpm_spec.spec_bump()
    function bumps the spec file for new release (via rpmdev-bumpspec)
    """

    if comment is None:
        comment = "automatic build by kentauros"

    # construct rpmdev-bumpspec command
    cmd = ["rpmdev-bumpspec"]

    # add --verbose or --quiet depending on settings
    if (get_verby() == 2) and not get_debug():
        cmd.append("--quiet")
    if (get_verby() == 0) or get_debug():
        cmd.append("--verbose")

    cmd.append(specfile)

    cmd.append('--comment=' + comment)

    log_command(LOGPREFIX1, "rpmdev-bumpspec", cmd, 1)
    subprocess.call(cmd)

