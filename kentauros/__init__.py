"""
kentauros package
"""

from enum import Enum


__all__ = ["actions",
           "bootstrap",
           "build",
           "config",
           "construct",
           "init",
           "package",
           "source",
           "upload"]


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"


class ActionType(Enum):
    """
    kentauros.actions.ActionType:
    enum containing all types of Action classes
    """
    VERIFY = 0
    GET = 1
    UPDATE = 2
    CONSTRUCT = 3
    BUILD = 4
    UPLOAD = 5
    CHAIN = 6
    CONFIG = 7
    CREATE = 8

