"""
kentauros.spec
"""

import os
import subprocess

from kentauros.base import dbg
from kentauros.base import get_date, goto_basedir, goto_pkgdir

from kentauros.conf import get_pkgvers, get_srctype
from kentauros.vcs import get_srcrev


def spec_moveto_old(pkgname):
    """
    kentauros.spec.spec_moveto_old()
    function that moves the package .spec file away (as backup or for overwriting)
    """
    dbg("Moving old .spec file away.")

    specfile_new = pkgname + ".spec"
    specfile_old = specfile_new + ".old"

    goto_pkgdir(pkgname)
    os.rename(specfile_new, specfile_old)
    goto_basedir()


def spec_moveto_new(pkgname):
    """
    kentauros.spec.spec_moveto_new()
    function that moves backup package .spec file back
    """
    dbg("Moving old .spec file back.")

    specfile_new = pkgname + ".spec"
    specfile_old = specfile_new + ".old"

    goto_pkgdir(pkgname)
    os.rename(specfile_old, specfile_new)
    goto_basedir()


def if_define_date(line):
    """
    kentauros.spec.if_define_date()
    function returns True if "%define date " is found on spec file line
    """
    if r"%define date " in line:
        return True
    else:
        return False


def of_define_date():
    """
    kentauros.spec.of_define_date()
    function returns a line defining the current date
    """
    date = get_date()
    return r"%define date " + date + "\n"


def if_define_rev(line):
    """
    kentauros.spec.if_define_rev()
    function returns True if "%define rev " is found on spec file line
    """
    if r"%define rev " in line:
        return True
    else:
        return False


def of_define_rev(rev):
    """
    kentauros.spec.of_define_rev()
    function returns a line defining the current revision
    """
    assert isinstance(rev, str)
    return r"%define rev " + rev + "\n"


def if_version(line):
    """
    kentauros.spec.if_version()
    function returns True if "Version: " is found on spec file line
    """
    if r"Version:" in line:
        return True
    else:
        return False


def format_spec_version(pkgname, ver):
    """
    kentauros.spec.format_spec_version()
    function that returns the package version in format for rpm spec files
    """
    srctype = get_srctype(pkgname)

    if srctype == "bzr":
        return ver + "~rev" + r"%{rev}"
    elif srctype == "git":
        return ver + "~git" + r"%{date}" + "~" + r"%{rev}"
    elif srctype == "url":
        return ver
    else:
        dbg("Source type is not supported.")


def of_version(pkgname, ver):
    """
    kentauros.spec.of_version()
    function returns a line with the version tag and the current version
    """
    return "Version: " + format_spec_version(pkgname, ver) + "\n"


def if_release(line):
    """
    kentauros.spec.if_release()
    function returns True if "Release: " is found on spec file line
    """
    if r"Release:" in line:
        return True
    else:
        return False


def of_release():
    """
    kentauros.spec.of_release()
    function returns a line with the release tag and release 0%{?dist}
    """
    return r"Release: 0%{?dist}" + "\n"


def spec_update(pkgname):
    """
    kentauros.spec.spec_update)
    function bumps the spec file for new version and / or revision
    moves old spec file to specfile.old as backup
    """
    spec_moveto_old(pkgname)
    ver = get_pkgvers(pkgname)
    rev = get_srcrev(pkgname)

    specname_new = pkgname + ".spec"
    specname_old = specname_new + ".old"

    goto_pkgdir(pkgname)

    specfile_old = open(specname_old, 'r')
    specfile_new = open(specname_new, 'x')

    for line in specfile_old:
        if if_define_rev(line):
            specfile_new.write(of_define_rev(rev))
        elif if_define_date(line):
            specfile_new.write(of_define_date())
        elif if_version(line):
            specfile_new.write(of_version(pkgname, ver))
        elif if_release(line):
            specfile_new.write(of_release())
        else:
            specfile_new.write(line)

    specfile_old.close()
    specfile_new.close()

    goto_basedir()


def spec_bump(pkgname, comment):
    """
    kentauros.spec.spec_bump()
    function bumps the spec file for new release (via rpmdev-bumpspec)
    """
    specname = pkgname + ".spec"
    commtstr = '--comment=' + comment

    goto_pkgdir(pkgname)
    subprocess.call(["rpmdev-bumpspec", commtstr, specname])
    goto_basedir()

