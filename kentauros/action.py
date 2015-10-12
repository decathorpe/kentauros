"""
kentauros.action
"""

from kentauros.check import pkg_check
from kentauros.check import src_check

from kentauros.conf import get_srctype

from kentauros.copr import copr_build

from kentauros.rpm import rpmbuild_create_dirs
from kentauros.rpm import rpmbuild_copy_sources
from kentauros.rpm import rpmbuild_build_srpm
from kentauros.rpm import rpmbuild_copy_result
from kentauros.rpm import rpmbuild_remove_dirs

from kentauros.spec import spec_bump
from kentauros.spec import spec_update

from kentauros.vcs import get_source
from kentauros.vcs import src_export
from kentauros.vcs import src_update


def package_update(package, refresh=False):
    """
    kentauros.action.package_update()
    This function is executed if the "update" sub-command is supplied to kentauros.
    """
    pkg_check(package)

    if refresh:
        print("Refreshing sources is not yet implemented.")
        src_export(package)

    if not src_check(package):
        update = get_source(package)

        if get_srctype(package) != "url":
            spec_update(package)

        src_export(package)

    else:
        update = src_update(package)
        if update:
            spec_update(package)
            spec_bump(package, "Update to new upstream snapshot.")
            src_export(package)

    return update


def package_build(package, force=False):
    """
    kentauros.action.package_build()
    This function is executed if the "build" sub-command is supplied to kentauros.
    """
    update = package_update(package, refresh=force)

    if update or force:
        rpmbuild_create_dirs()
        rpmbuild_copy_sources(package)
        rpmbuild_build_srpm(package)
        rpmbuild_copy_result(package)
        rpmbuild_remove_dirs()

    if update:
        return update
    else:
        return None


def package_upload(package, watch=False, force=False):
    """
    kentauros.action.package_upload()
    This function is executed if the "upload" sub-command is supplied to kentauros.
    """

    build = package_build(package, force)

    if build or force:
        copr_build(package, watch)
        return build
    else:
        return None


#def package_bump(pkgname, bumpreason=None):
def package_bump():
    """
    kentauros.action.package_bump()
    This function bumps the "Release" field of .spec files and supplies
    changelog information ("Version bump because of: $bumpreason changes.").
    """


#def package_verify(pkgname):
def package_verify():
    """
    kentauros.action.package_verify()
    This function is executed if the "verify" sub-command is supplied to kentauros.
    """

    return True

