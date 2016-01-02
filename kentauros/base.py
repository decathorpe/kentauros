"""
kentauros.base
"""

import enum
import os
import sys

from kentauros.cli import DEBUG


# check if being run as root (EUID == 0)
ROOT = not bool(os.geteuid())

# get user running ktr
USER = os.getenv('USER')

# get user home
HOME = os.path.join("/home/", USER)


SUPPORTED_ARCHIVE_TYPES = ["*.tar.gz", "*.tar.xz"]


class SrcType(enum.Enum):
    """
    kentauros.pkgconf.SrcType
    class (Enum) that contains all supported source types
    """
    local = 1
    url = 2
    git = 3
    bzr = 4


def dbg(msg):
    """
    kentauros.dbg()
    prints debug messages if DEBUG is True (set by --verbose or --debug)
    """
    if DEBUG:
        print("DEBUG: " + str(msg))


def err(msg):
    """
    kentauros.err()
    prints error messages to sys.stderr. format: ERROR: >message>
    """

    print("ERROR: " + msg, file=sys.stderr)

