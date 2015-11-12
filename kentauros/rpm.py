"""
kentauros.rpm
"""

import os
import glob
import shutil
import subprocess

from kentauros.base import HOME, BASEDIR, SUPPORTED_ARCHIVE_TYPES
from kentauros.base import goto_basedir, goto_pkgdir
from kentauros.check import home_check


RPMBUILD_DIR = os.path.join(HOME, "rpmbuild")
RPMBUILD_OLD = os.path.join(HOME, "rpmbuild_old")
RPMBUILD_SOURCES = os.path.join(RPMBUILD_DIR, "SOURCES")
RPMBUILD_SPECS = os.path.join(RPMBUILD_DIR, "SPECS")
RPMBUILD_SRPMS = os.path.join(RPMBUILD_DIR, "SRPMS")


def check_rpmbuild():
    """
    kentauros.rpm.check_rpmbuild()
    function that checks $HOME/rpmbuild, rpmbuild/SOURCES and rpmbuild/SPECS
    for existence and writability
    """
    home_check()

    if not os.access(RPMBUILD_DIR, os.W_OK):
        raise OSError("rpmbuild directory not existent or not writable.")
    if not os.access(RPMBUILD_SOURCES, os.W_OK):
        raise OSError("rpmbuild SOURCES directory not existent or not writable.")
    if not os.access(RPMBUILD_SPECS, os.W_OK):
        raise OSError("rpmbuild SPECS directory not existent or not writable.")
    if not os.access(RPMBUILD_SRPMS, os.W_OK):
        raise OSError("rpmbuild SRPMS directory not existent or not writable.")

def rpmbuild_create_dirs():
    """
    kentauros.rpm.rpmbuild_create_dirs()
    function that creates neccessary directories for rpmbuild:
    $HOME/rpmbuild/SOURCES, $HOME/rpmbuild/SPECS
    moves away pre-existing rpmbuild directory to rpmbuild_old
    """
    home_check()

    if os.path.exists(RPMBUILD_DIR):
        shutil.move(RPMBUILD_DIR, RPMBUILD_OLD)
        print("Moved old rpmbuild directory away.")

    os.mkdir(RPMBUILD_DIR)
    os.mkdir(RPMBUILD_SPECS)
    os.mkdir(RPMBUILD_SRPMS)
    os.mkdir(RPMBUILD_SOURCES)

def rpmbuild_remove_dirs():
    """
    kentauros.rpm.rpmbuild_remove_dirs()
    function that removes temporary directories for rpmbuild
    moves back pre-existing rpmbuild directory to rpmbuild_old
    """
    home_check()

    if os.path.exists(RPMBUILD_DIR):
        shutil.rmtree(RPMBUILD_DIR)

    if os.path.exists(RPMBUILD_OLD):
        shutil.move(RPMBUILD_OLD, RPMBUILD_DIR)
        print("Moved old rpmbuild backup back into original place.")

def rpmbuild_copy_sources(pkgname):
    """
    kentauros.rpm.rpmbuild_copy_sources()
    function that copies sources and spec files to rpmbuild directory
    """
    check_rpmbuild()

    goto_pkgdir(pkgname)

    conf_file = pkgname + ".conf"
    spec_file = pkgname + ".spec"

    patches = glob.glob("*.patch")
    sources = list()

    for archive_type in SUPPORTED_ARCHIVE_TYPES:
        archive_list = glob.glob(archive_type)
        for archive in archive_list:
            sources.append(archive)

    for patch in patches:
        subprocess.call(["cp", patch, RPMBUILD_SOURCES])

    for source in sources:
        subprocess.call(["mv", source, RPMBUILD_SOURCES])

    subprocess.call(["cp", conf_file, RPMBUILD_SOURCES])
    subprocess.call(["cp", spec_file, RPMBUILD_SPECS])

    goto_basedir()


def rpmbuild_build_srpm(pkgname):
    """
    kentauros.rpm.rpmbuild_build_srpm()
    function that builds srpm in rpmbuild/SRPMS
    prerequisite: execution of rpmbuild_copy_sources()
    """
    check_rpmbuild()

    os.chdir(RPMBUILD_SPECS)
    subprocess.call(["rpmbuild", "-bs", "./" + pkgname + ".spec"])
    goto_basedir()

def rpmbuild_copy_result(pkgname):
    """
    kentauros.rpm.rpmbuild_copy_result()
    function that copies built srpm files to package directory
    """
    check_rpmbuild()

    pkgdir = os.path.join(BASEDIR, pkgname)

    os.chdir(RPMBUILD_SRPMS)

    src_rpms = glob.glob("*.src.rpm")

    for src_rpm in src_rpms:
        subprocess.call(["cp", src_rpm, pkgdir])

    goto_basedir()


