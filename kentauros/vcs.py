"""
kentauros.vcs
"""


from kentauros.base import dbg

from kentauros.bzr import get_srcrev_bzr, get_source_bzr, src_update_bzr
from kentauros.bzr import src_export_bzr, format_version_bzr

from kentauros.git import get_srcrev_git, get_source_git, src_update_git
from kentauros.git import src_export_git, format_version_git

from kentauros.url import get_source_url, format_version_url

from kentauros.conf import get_pkgvers, get_srcname, get_srctype
from kentauros.conf import get_srcorig, get_srckeep


def format_version(pkgname, ver, rev):
    """
    kentauros.vcs.format_version()
    generic function that returns the package version in a standard format
    """
    srctype = get_srctype(pkgname)

    if srctype == "bzr":
        return format_version_bzr(ver, rev)
    elif srctype == "git":
        return format_version_git(ver, rev)
    elif srctype == "url":
        return format_version_url(ver)
    else:
        dbg("Source type is not supported.")


def get_srcrev(pkgname):
    """
    kentauros.vcs.get_srcrev()
    generic function that returns the current revision number / commit id
    """
    dbg("Checking revision number / commit id.")
    srcname = get_srcname(pkgname)
    srctype = get_srctype(pkgname)

    if srctype == "bzr":
        return get_srcrev_bzr(pkgname, srcname)
    elif srctype == "git":
        return get_srcrev_git(pkgname, srcname)
    else:
        return None

def get_source(pkgname):
    """
    kentauros.vcs.get_source()
    generic function that downloads the specified sources from vcs
    """
    srctype = get_srctype(pkgname)
    srcorig = get_srcorig(pkgname)
    srcdest = get_srcname(pkgname)
    srckeep = get_srckeep(pkgname)

    if srctype == "bzr":
        return get_source_bzr(pkgname, srcorig, srcdest, srckeep)
    elif srctype == "git":
        return get_source_git(pkgname, srcorig, srcdest, srckeep)
    elif srctype == "url":
        return get_source_url(pkgname, srcorig, srcdest)
    else:
        dbg("Source type is not supported.")

def src_update(pkgname):
    """
    kentauros.vcs.src_update()
    generic function that updates the specified vcs repository
    """
    srcname = get_srcname(pkgname)
    srctype = get_srctype(pkgname)

    dbg("Checking " + srcname + " " + srctype + " repo for updates.")

    if srctype == "bzr":
        return src_update_bzr(pkgname, srcname)
    elif srctype == "git":
        return src_update_git(pkgname, srcname)
    elif srctype == "url":
        return 0
    else:
        dbg("Source type is not supported.")
        return 0

def src_export(pkgname):
    """
    kentauros.vcs.src_export()
    function that exports the specified vcs repository to a tar.gz archive
    """
    pkgvers = get_pkgvers(pkgname)
    srcname = get_srcname(pkgname)
    srctype = get_srctype(pkgname)

    dbg("Exporting " + pkgname + "VCS sources to tarball for use in packaging.")

    if srctype == "bzr":
        src_export_bzr(pkgname, srcname, pkgvers)
    elif srctype == "git":
        src_export_git(pkgname, srcname, pkgvers)
    elif srctype == "url":
        pass
    else:
        dbg("Source type is not supported.")

