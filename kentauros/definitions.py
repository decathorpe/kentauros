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

from enum import Enum


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"


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


class BuilderType(Enum):
    """
    kentauros.definitons.BuilderType:
    enum that describes the kind of constructors supported
    """
    MOCK = 0


class ConstructorType(Enum):
    """
    kentauros.definitons.ConstructorType:
    enum that describes the kind of constructors supported
    """
    SRPM = 0


class SourceType(Enum):
    """
    kentauros.definitons.SourceType:
    enum that describes the kind of package sources supported
    """
    LOCAL = 0
    URL = 1
    GIT = 2
    BZR = 3


class UploaderType(Enum):
    """
    kentauros.definitons.UploaderType:
    enum that describes the kind of uploaders supported
    """
    COPR = 0

