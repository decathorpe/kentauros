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
    EXPORT = 3
    CONSTRUCT = 4
    BUILD = 5
    UPLOAD = 6
    CHAIN = 7
    CONFIG = 8
    CREATE = 9

