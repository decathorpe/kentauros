"""
This module contains all definitions of types and global variables that are
used by nearly every other module / subpackage.

It includes these globally used variables:

* ``KTR_SYSTEM_DATADIR``:       directory where kentauros data is installed to /
  resides when installed
* ``KTR_VERSION``:              this version string is used when installing and
  packaging kentauros

The following Enums are defined here:

* :py:class:`KtrConfType`:      types of kentauros configuration source
* :py:class:`ActionType`:       types of actions that can be executed
* :py:class:`BuilderType`:      types of supported binary package builders
* :py:class:`ConstructorType`:  types of supported source package constructors
* :py:class:`InstanceType`:     types of kentauros instances
* :py:class:`SourceType`:       types of supported package sources
* :py:class:`UploaderType`:     types of supported package uploaders
"""


from enum import Enum, unique


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"
"""This string represents the absolute path which kentauros data files are
copied to at installation and where they are expected to be when running ktr.
"""

KTR_VERSION = "0.9.11"
"""This string represents the version string used by ``setup.py`` at install
time and ``make-srpm.sh`` when building an srpm package. The version in
``kentauros.spec`` has to be set manually yet.
"""


class KtrConfType(Enum):
    """
    This Enum defines the types of configuration file locations kentauros
    supports and tries to read from. For all of them, their full qualifier and
    a 3-letter abbreviation (if longer than 3 letters) is given for comfort.
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
    This Enum defines the different types of actions that are supported by
    kentauros. This includes a default ``NONE`` type and a fallback ``DUMMY``
    type.
    """

    NONE = 0
    DUMMY = 1
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
    This Enum defines the different types of binary package builders that are
    supported by kentauros. At the moment, only ``mock`` is supported for
    building binary packages locally. It also includes a default ``NONE`` type
    and a fallback ``DUMMY`` type.
    """

    NONE = 0
    DUMMY = 1
    MOCK = 2


@unique
class ConstructorType(Enum):
    """
    This Enum defines the different types of source package builders that are
    supported by kentauros. At the moment, only ``srpm`` packages are supported
    as source packages. It also includes a default ``NONE`` type and a fallback
    ``DUMMY`` type.
    """

    NONE = 0
    DUMMY = 1
    SRPM = 2


@unique
class InstanceType(Enum):
    """
    This Enum defines the different modes in which kentauros can be run (as
    imported from different scripts). This includes ``NORMAL`` invocation for
    most standard actions, ``CONFIG`` for changing package-specific
    configuration values and ``CREATE`` for creating package configuration files
    from templates.
    """

    NORMAL = 0
    CONFIG = 1
    CREATE = 2


@unique
class SourceType(Enum):
    """
    This Enum defines the different types of package source sources that are
    supported by kentauros. At the moment, ``local``, ``url``, ``git`` and
    ``bzr`` sources are supported. It also includes a default ``NONE`` type and
    a fallback ``DUMMY`` type.
    """

    NONE = 0
    DUMMY = 1
    URL = 2
    GIT = 3
    BZR = 4
    LOCAL = 5


@unique
class UploaderType(Enum):
    """
    This Enum defines the different types of (source) package uploaders that are
    supported by kentauros. At the moment, only source packages can be uploaded,
    and only to ``copr``. It also includes a default ``NONE`` type and a
    fallback ``DUMMY`` type.
    """

    NONE = 0
    DUMMY = 1
    COPR = 2

