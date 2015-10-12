"""
kentauros.git
"""

import subprocess

from kentauros.cli import DEBUG
from kentauros.base import dbg, get_date
from kentauros.base import goto_basedir, goto_pkgdir, goto_srcdir

from kentauros.conf import get_srcname


def format_version_git(ver, rev):
    """
    kentauros.git.format_version_git()
    function that returns the package version in a standard format
    """
    assert isinstance(ver, str)
    assert isinstance(rev, str)
    date = get_date()

    # this evaluates to e.g. 11.1.0~devel~git20150903~34af7e2b
    return ver + "~git" + date + "~" + rev


def get_srcrev_git(pkgname, srcname):
    """
    kentauros.git.get_srcrev_git()
    function that returns the current commit id of the repository
    """
    goto_srcdir(pkgname, srcname)
    rev = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode()
    rev = rev.rstrip('\r\n')[0:8]
    goto_basedir()

    dbg(pkgname + " repo is at commit: " + rev)
    return rev


def get_source_git(pkgname, orig, dest, keep=True):
    """
    kentauros.git.get_source_git()
    function that downloads the specified git repository (whole or shallow)
    """
    srcname = get_srcname(pkgname)
    dbg("Checking out git repository " + orig + " to directory " + dest + ".")

    quietstr = "--quiet"
    if DEBUG:
        quietstr = "--verbose"

    goto_pkgdir(pkgname)
    if keep:
        subprocess.call(["git", "clone", quietstr, orig, dest])
    else:
        subprocess.call(["git", "clone", "--depth=1", quietstr, orig, dest])
    goto_basedir()

    dbg("Checkout to " + dest + " successful.")
    rev = get_srcrev_git(pkgname, srcname)
    dbg("Revision of checkout: " + rev)

    return rev


def src_update_git(pkgname, srcname):
    """
    kentauros.git.src_update_git()
    function that updates the specified git repository
    """
    rev_old = get_srcrev_git(pkgname, srcname)

    goto_srcdir(pkgname, srcname)
    if DEBUG:
        subprocess.call(["git", "pull", "--rebase"])
    else:
        subprocess.call(["git", "pull", "--rebase", "--quiet"])
    goto_basedir()

    rev_new = get_srcrev_git(pkgname, srcname)

    if rev_new != rev_old:
        return rev_new
    else:
        return 0


def src_export_git(pkgname, srcname, pkgvers, keep=True):
    """
    kentauros.git.src_export_git()
    function that exports the specified git repository
    """
    rev = get_srcrev_git(pkgname, srcname)

    version_str = format_version_git(pkgvers, rev)
    pkgpver_str = pkgname + "-" + version_str

    prefix_str = "--prefix=" + pkgpver_str + "/"
    target_str = "../" + pkgpver_str + ".tar.gz"

    goto_srcdir(pkgname, srcname)
    ret_code = subprocess.call(["git", "archive", prefix_str, "HEAD", "--output", target_str])
    if not keep:
        subprocess.call(["rm", "-r", srcname])
    goto_basedir()

    if ret_code:
        print("ERROR: Export to " + target_str + ".tar.gz not successful.")
    else:
        dbg("Export to " + target_str + ".tar.gz successful.")

