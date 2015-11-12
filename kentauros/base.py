"""
kentauros.base
"""

# import appdirs
import os
import subprocess

from kentauros.cli import DEBUG


BASEDIR = os.getcwd()
HOME = os.environ['HOME']

SUPPORTED_ARCHIVE_TYPES = [".tar.gz", ".tar.xz"]


def dbg(msg):
    """
    kentauros.dbg()
    prints debug messages if DEBUG is True (set by --verbose or --debug)
    """
    if DEBUG:
        print("DEBUG: " + str(msg))


def get_date():
    """
    kentauros.get_date()
    returns date in YYMMDD format as string
    """
    date = subprocess.check_output(["date", r"+%y%m%d"]).decode().rstrip('\n\r')
    return date


def goto_pkgdir(pkgname):
    """
    kentauros.goto_pkgdir
    function that changes the CWD to the package directory
    """
    dbg("Changing to package directory: " + pkgname)
    pkg = os.path.join(BASEDIR, pkgname)

    if os.access(pkg, os.W_OK):
        os.chdir(pkg)
    else:
        raise OSError("Package directory not accessible or non-existent.")

def goto_srcdir(pkgname, srcname):
    """
    kentauros.goto_src
    function that changes the CWD to the package source directory
    """
    dbg("Changing to source directory: " + pkgname + "/" + srcname)
    src = os.path.join(BASEDIR, pkgname, srcname)

    if os.access(src, os.W_OK):
        os.chdir(src)
    else:
        raise OSError("Source directory not accessible or non-existent.")

def goto_basedir():
    """
    kentauros.goto_basedir
    function that resets the CWD to the base directory
    """
    dbg("Changing to base directory: " + BASEDIR)
    if os.access(BASEDIR, os.W_OK):
        os.chdir(BASEDIR)
    else:
        raise OSError("Base directory not writable or vanished.")




