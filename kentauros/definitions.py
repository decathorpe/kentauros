"""
kentauros.definitions module
contains definition of ktr system datadir used everywhere and
enum definitions for:
- ktr configuration types
- ktr action types
- builder types
- constructor types
- source types
- uploader types
"""

from enum import Enum, unique


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"


@unique
class KtrConfType(Enum):
    """
    kentauros.definitions.KtrConfType
    enum that defines all possible configuration sources.
    """
    CLI = 0
    ENV = 1
    PROJECT = 2
    USER = 3
    SYSTEM = 4
    DEFAULT = 5
    FALLBACK = 6


@unique
class ActionType(Enum):
    """
    kentauros.definitions.ActionType:
    enum containing all types of Action classes
    """
    CREATE = 10
    STATUS = 11
    CONFIG = 12
    VERIFY = 13
    GET = 20
    UPDATE = 21
    EXPORT = 22
    CLEAN = 23
    REFRESH = 24
    PREPARE = 25
    CONSTRUCT = 30
    BUILD = 40
    UPLOAD = 50
    CHAIN = 60


@unique
class BuilderType(Enum):
    """
    kentauros.definitons.BuilderType:
    enum that describes the kind of constructors supported
    """
    NONE = 0
    MOCK = 1


@unique
class ConstructorType(Enum):
    """
    kentauros.definitons.ConstructorType:
    enum that describes the kind of constructors supported
    """
    NONE = 0
    SRPM = 1


@unique
class SourceType(Enum):
    """
    kentauros.definitons.SourceType:
    enum that describes the kind of package sources supported
    """
    NONE = 0
    URL = 1
    GIT = 2
    BZR = 3
    LOCAL = 4


@unique
class UploaderType(Enum):
    """
    kentauros.definitons.UploaderType:
    enum that describes the kind of uploaders supported
    """
    NONE = 0
    COPR = 1

