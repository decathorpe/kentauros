"""
kentauros.definitions module
- definition of ktr system datadir used everywhere
- enum definitions for
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
    BUILD = 0
    CHAIN = 1
    CLEAN = 2
    CONFIG = 3
    CONSTRUCT = 4
    CREATE = 5
    EXPORT = 6
    GET = 7
    REFRESH = 8
    STATUS = 9
    UPDATE = 10
    UPLOAD = 11
    VERIFY = 12


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

