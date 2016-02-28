"""
kentauros.definitions module
"""

from enum import Enum


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"


class KtrConfType(Enum):
    """
    kentauros.definitions.KtrConfType
    enum that defines all possible configuration sources.
    """
    CLI = 1
    ENV = 2
    PROJECT = 3
    USER = 4
    SYSTEM = 5
    DEFAULT = 6
    FALLBACK = 7


class SourceType(Enum):
    """
    kentauros.source.common.SourceType
    enum that describes the kind of package sources supported
    """
    LOCAL = 1
    URL = 2
    GIT = 3
    BZR = 4


class ActionType(Enum):
    """
    kentauros.definitions.ActionType:
    enum containing all types of Action classes
    """
    BUILD = 0
    CHAIN = 1
    CLEAN = 2
    CONFIG = 3
    CONSTRUCT = 4
    CREATE = 5
    EXPORT = 6
    GET = 7
    REFRESH = 8
    UPDATE = 9
    UPLOAD = 10
    VERIFY = 11

