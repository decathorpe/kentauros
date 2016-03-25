"""
# TODO: napoleon docstring
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


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"    # TODO: napoleon docstring
KTR_VERSION = "0.9.4"                           # TODO: napoleon docstring


class KtrConfType(Enum):
    """
    # TODO: napoleon docstring
    kentauros.definitions.KtrConfType
    enum that defines all possible configuration sources.
    """

    CLI = 0
    ENV = 1
    PRJ = 2
    PROJECT = 2
    USER = 3
    USR = 3
    SYS = 4
    SYSTEM = 4
    DEF = 5
    DEFAULT = 5
    FBK = 6
    FALLBACK = 6


@unique
class ActionType(Enum):
    """
    # TODO: napoleon docstring
    kentauros.definitions.ActionType:
    enum containing all types of Action classes
    """

    NONE = 0
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
    # TODO: napoleon docstring
    kentauros.definitons.BuilderType:
    enum that describes the kind of constructors supported
    """

    NONE = 0
    MOCK = 1


@unique
class ConstructorType(Enum):
    """
    # TODO: napoleon docstring
    kentauros.definitons.ConstructorType:
    enum that describes the kind of constructors supported
    """

    NONE = 0
    SRPM = 1


@unique
class InstanceType(Enum):
    """
    # TODO: napoleon docstring
    kentauros.definitions.InstanceType:
    enum that describes whether ktr, ktr-config or ktr-create has been invoked
    """

    NORMAL = 0
    CONFIG = 1
    CREATE = 2


@unique
class SourceType(Enum):
    """
    # TODO: napoleon docstring
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
    # TODO: napoleon docstring
    kentauros.definitons.UploaderType:
    enum that describes the kind of uploaders supported
    """

    NONE = 0
    COPR = 1

