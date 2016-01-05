"""
kentauros.bzr
"""

import subprocess

from kentauros.cli import DEBUG
from kentauros.base import dbg
from kentauros.base import goto_basedir, goto_pkgdir, goto_srcdir

from kentauros.conf import get_srcname


def format_version_bzr(ver, rev):
    """
    kentauros.bzr.format_version_bzr()
    function that returns the package version in a standard format
    """
    assert isinstance(ver, str)
    assert isinstance(rev, str)
    return ver + "~rev" + rev


def get_srcrev_bzr(pkgname, srcname):
    """
    kentauros.bzr.get_srcrev_bzr()
    function that returns the current revision number of the source branch
    """
    goto_srcdir(pkgname, srcname)
    rev = subprocess.check_output(["bzr", "revno"]).decode().rstrip('\n\r')
    goto_basedir()

    dbg(pkgname + " repo is at revno: " + rev)
    return rev


def get_source_bzr(pkgname, orig, dest, keep=True):
    """
    kentauros.bzr.get_source_bzr()
    function that downloads the specified bzr branch or lightweight checkout
    """
    srcname = get_srcname(pkgname)
    dbg("Checking out bzr repository " + orig + " to directory " + dest + ".")
    dbg("Keeping sources: " + str(keep))

    quietstr = "--quiet"
    if DEBUG:
        quietstr = "--verbose"

    goto_pkgdir(pkgname)
    if keep:
        subprocess.call(["bzr", "branch", quietstr, orig, "./" + dest])
    else:
        subprocess.call(["bzr", "checkout", "--lightweight", quietstr, orig, "./" + dest])
    goto_basedir()

    dbg("Checkout to " + dest + " successful.")
    rev = get_srcrev_bzr(pkgname, srcname)
    dbg("Revision number of checkout: " + rev)

    return rev


def src_update_bzr(pkgname, srcname):
    """
    kentauros.bzr.src_update_bzr()
    function that updates the specified bzr branch or lightweight checkout
    """

    rev_old = get_srcrev_bzr(pkgname, srcname)

    goto_srcdir(pkgname, srcname)
    if DEBUG:
        subprocess.call(["bzr", "pull"])
    else:
        subprocess.call(["bzr", "pull", "--quiet"])
    goto_basedir()

    rev_new = get_srcrev_bzr(pkgname, srcname)

    if rev_new != rev_old:
        return rev_new
    else:
        return 0


def src_export_bzr(pkgname, srcname, pkgvers, keep=True):
    """
    kentauros.bzr.src_export_bzr()
    function that exports the specified bzr branch or lightweight checkout
    to a .tar.gz archive
    """
    rev = get_srcrev_bzr(pkgname, srcname)

    strvers = format_version_bzr(pkgvers, rev)
    strpkgv = pkgname + "-" + strvers

    filename = "../" + strpkgv + ".tar.gz"

    goto_srcdir(pkgname, srcname)
    subprocess.call(["bzr", "export", filename])
    if not keep:
        subprocess.call(["rm", "-r", srcname])
    goto_basedir()

    dbg("Export to ../" + strpkgv + ".tar.gz successful.")

