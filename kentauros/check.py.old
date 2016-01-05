"""
kentauros.check
"""

import os

from kentauros.base import HOME, BASEDIR
from kentauros.conf import get_srcname


def pkg_check(pkgname):
    """
    kentauros.check.pkg_check
    function to check for package directory and config file existence
    also checks for config file readability and package dir writability
    """
    confpath = os.path.join(BASEDIR, pkgname, pkgname + ".conf")

    if not os.access(pkgname, os.W_OK):
        raise OSError("Package directory does not exist or is inaccessible.")

    if not os.access(confpath, os.R_OK):
        raise OSError("Package .conf does not exist or is inaccessible.")

def src_check(pkgname):
    """
    kentauros.check.src_check
    function to check for package source directory
    also checks for package source dir writability
    """
    srcname = get_srcname(pkgname)
    srcdir = os.path.join(BASEDIR, pkgname, srcname)

    if not os.access(srcdir, os.W_OK):
#        raise OSError("Source directory does not exist or is inaccessible.")
        return False

    return True

def home_check():
    """
    kentauros.check.home_check
    function to check for user home directory
    also checks for dir writability
    """

    if not os.access(HOME, os.W_OK):
        raise OSError("Home directory is not writable.")

