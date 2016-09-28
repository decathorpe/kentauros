"""
This module contains all definitions of types and global variables that are used by nearly every
other module / subpackage.

It includes these globally used variables:

* ``KTR_SYSTEM_DATADIR``:   directory where kentauros data is installed to resides when installed
* ``KTR_VERSION``:          this version string is used when installing and packaging kentauros

The following Enums are defined here:

* :py:class:`KtrConfType`:      types of kentauros configuration source
* :py:class:`ActionType`:       types of actions that can be executed
* :py:class:`BuilderType`:      types of supported binary package builders
* :py:class:`ConstructorType`:  types of supported source package constructors
* :py:class:`SourceType`:       types of supported package sources
* :py:class:`UploaderType`:     types of supported package uploaders
"""


from enum import Enum, unique


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"
"""This string represents the absolute path which kentauros data files are
copied to at installation and where they are expected to be when running ktr.
"""

KTR_VERSION = "0.9.90"
"""This string represents the version string used by ``setup.py`` at install
time and ``make-srpm.sh`` when building an srpm package. The version in
``kentauros.spec`` has to be set manually yet.
"""


class KtrConfType(Enum):
    """
    This Enum defines the types of configuration file locations kentauros supports and tries to read
    from. For all of them, their full qualifier and a 3-letter abbreviation (if longer than 3
    letters) is given for comfort.
    """

    CLI = 0
    ENV = 1
    PRJ = 2
    USR = 3
    SYS = 4
    DEF = 5
    FBK = 6

    PROJECT = 2
    USER = 3
    SYSTEM = 4
    DEFAULT = 5
    FALLBACK = 6


@unique
class ActionType(Enum):
    """
    This Enum defines the different types of actions that are supported by kentauros. This includes
    a default *NONE* type.
    """

    NONE = 0
    IMPORT = 10
    STATUS = 11
    VERIFY = 12
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
    This Enum defines the different types of binary package builders that are supported by
    kentauros. It also includes a default *NONE* type.
    """

    NONE = 0
    MOCK = 1


@unique
class ConstructorType(Enum):
    """
    This Enum defines the different types of source package builders that are supported by
    kentauros. It also includes a default *NONE* type.
    """

    NONE = 0
    SRPM = 1


@unique
class SourceType(Enum):
    """
    This Enum defines the different types of package source sources that are supported by kentauros.
    It also includes a default *NONE* type.
    """

    NONE = 0
    URL = 10
    GIT = 20
    BZR = 21
    LOCAL = 30


@unique
class UploaderType(Enum):
    """
    This Enum defines the different types of (source) package uploaders that are supported by
    kentauros. It also includes a default *NONE* type.
    """

    NONE = 0
    COPR = 1
