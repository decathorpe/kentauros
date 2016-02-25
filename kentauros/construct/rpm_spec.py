"""
kentauros.construct.rpm_spec
contains helper functions for building rpm source packages
"""

import subprocess

from kentauros.init import DEBUG, VERBY, log_command
from kentauros.source.common import SourceType


LOGPREFIX1 = "ktr/construct/rpm_spec: "


def if_version(line):
    """
    kentauros.construct.rpm_spec.if_version()
    function returns True if "Version: " is found on spec file line
    """
    if line[0:8] == "Version:":
        return True
    else:
        return False


def of_version(package):
    """
    kentauros.construct.rpm_spec.of_version()
    function returns a line with the version tag and the current version
    """
    # TODO: use dict of functions for different enum members of SourceType
    if package.source.type == SourceType.GIT:
        verstr = "Version:" + 8 * " " + package.source.get_version() + "~git%{date}~%{rev}" + "\n"
    elif package.source.type == SourceType.BZR:
        verstr = "Version:" + 8 * " " + package.source.get_version() + "~rev%{rev}" + "\n"
    else:
        verstr = "Version:" + 8 * " " + package.source.get_version() + "\n"
    return verstr


def if_release(line):
    """
    kentauros.construct.rpm_spec.if_release()
    function returns True if "Release: " is found on spec file line
    """
    if line[0:8] == "Release:":
        return True
    else:
        return False


def of_release(num=0, dist=True):
    """
    kentauros.construct.rpm_spec.of_release()
    function returns a line with the release tag and 0%{?dist} if dist is True
    """
    assert isinstance(num, int)

    if dist:
        return "Release:" + 8 * " " + str(num) + "%{dist}" + "\n"
    else:
        return "Release:" + 8 * " " + str(num) + "\n"


def munge_line(line, package):
    """
    kentauros.construct.rpm_spec.munge_line()
    function returns a munged line if given a line
    """

    if if_version(line):
        return of_version(package)
    if if_release(line):
        return of_release()
    return line


def spec_bump(specfile, comment=None):
    """
    kentauros.construct.rpm_spec.spec_bump()
    function bumps the spec file for new release (via rpmdev-bumpspec)
    """

    if comment == None:
        comment = "automatic build by kentauros"

    # construct rpmdev-bumpspec command
    cmd = ["rpmdev-bumpspec"]

    # add --verbose or --quiet depending on settings
    if (VERBY == 2) and not DEBUG:
        cmd.append("--quiet")
    if (VERBY == 0) or DEBUG:
        cmd.append("--verbose")

    cmd.append(specfile)

    cmd.append('--comment=' + comment)

    log_command(LOGPREFIX1, "rpmdev-bumpspec", cmd, 1)
    subprocess.call(cmd)

