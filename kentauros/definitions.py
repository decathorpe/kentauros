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
* :py:class:`UploaderType`:     types of supported package upload modules
"""


from enum import Enum, unique


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"
"""This string represents the absolute path which kentauros data files are
copied to at installation and where they are expected to be when running ktr.
"""

KTR_VERSION = "0.9.94"
"""This string represents the version string used by ``setup.py`` at install
time and ``make-srpm.sh`` when building an srpm package. The version in
``kentauros.spec`` has to be set manually yet.
"""


@unique
class PkgModuleType(Enum):
    """
    This Enum defines the types of package submodules there can be.
    """

    SOURCE = 1
    CONSTRUCTOR = 2
    BUILDER = 3
    UPLOADER = 4


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

    PREPARE = 20
    CONSTRUCT = 21
    BUILD = 22
    UPLOAD = 23

    CLEAN = 30
    CHAIN = 40


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
    This Enum defines the different types of (source) package uploader modules that are supported by
    kentauros. It also includes a default *NONE* type.
    """

    NONE = 0
    COPR = 1
