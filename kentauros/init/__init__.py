"""
kentauros.config module
explicitly determines order in which configurations are read.
later items in the list can override already determined configuration,
or act as fallback if none has been found so far.
"""

import os

from kentauros.base import err, ROOT, USER, HOME
from kentauros.config import KTR_CONF


__all__ = []

# base directories for being run as user and as root
SYSBASEDIR = KTR_CONF.sysbasedir
SYSCONFDIR = KTR_CONF.sysconfdir
SYSDATADIR = KTR_CONF.sysdatadir

USRBASEDIR = KTR_CONF.usrbasedir
USRCONFDIR = KTR_CONF.usrconfdir
USRDATADIR = KTR_CONF.usrdatadir

# define base directories depending on whether being run as root or not
if not ROOT:
    BASEDIR = USRBASEDIR
    CONFDIR = USRCONFDIR
    DATADIR = USRDATADIR
else:
    BASEDIR = SYSBASEDIR
    CONFDIR = SYSCONFDIR
    DATADIR = SYSDATADIR


def __init_dirs__(basedir, confdir, datadir):
    if not os.access(basedir, os.R_OK):
        os.mkdir(basedir)
    if not os.access(confdir, os.W_OK):
        os.mkdir(confdir)
    if not os.access(datadir, os.W_OK):
        os.mkdir(datadir)


def ktr_init():
    """
    kentauros.init.ktr_init()
    read configuration, initialise directories, etc.
    """
    if ROOT:
        print("Running as root is discouraged.")

    try:
        __init_dirs__(BASEDIR, CONFDIR, DATADIR)
    except OSError:
        err("Initialisation failed. Could not create kentauros directories.")
        raise SystemExit

