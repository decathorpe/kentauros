"""
This subpackage contains the :py:class:`Package` class, which holds package configuration parsed
from the corresponding `package.conf` file (errors that occur during parsing are probably not
handled correctly yet). After parsing the package configuration, :py:class:`Source`,
:py:class:`Constructor`, :py:class:`Builder` and :py:class:`Uploader` instances are set as
attributes according to configuration.
"""


import os

from collections import OrderedDict
from configparser import ConfigParser

from kentauros.definitions import PkgModuleType
from kentauros.definitions import BuilderType, ConstructorType, SourceType, UploaderType
from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.modules import PKG_MODULE_DICT, PKG_MODULE_TYPE_DICT

# from kentauros.modules.builder import BUILDER_TYPE_DICT
# from kentauros.modules.constructor import CONSTRUCTOR_TYPE_DICT
# from kentauros.modules.sources import SOURCE_TYPE_DICT
# from kentauros.modules.uploader import UPLOADER_TYPE_DICT


LOGPREFIX = "ktr/package"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class PackageError(Exception):
    """
    This custom exception will be raised when errors occur during parsing of a package .conf file.

    Arguments:
        str value: informational string accompanying the exception
    """

    def __init__(self, value: str=""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class Package:
    """
    This class envelops all things necessary to perform actions on a specific "package" of software.

    Arguments:
        str conf_name:              name of the configuration file, without the ".conf" suffix

    Attributes:
        str conf_name:              name of the configuration
        str name:                   name of the package
        ConfigParser conf:          parser for package.conf file
        Source source:              handling of upstream source code
        Constructor constructor:    handling of building compilable source packages
        Builder builder:            handling of building binary packages from source
        Uploader uploader:          handling of uploading source/binary packages to remote location

    Raises:
        PackageError:               error if package.conf file is invalid
    """

    def __init__(self, conf_name: str):
        assert isinstance(conf_name, str)

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        self.file = os.path.join(ktr.conf.get_confdir(), conf_name + ".conf")
        self.conf = ConfigParser()
        self.conf_name = conf_name

        if not os.path.exists(self.file):
            raise FileNotFoundError("Package configuration file does not exist.")

        success = self.conf.read(self.file)
        if not success:
            logger.err("Package configuration could not be read.")
            logger.err("Path: " + self.file)
            raise PackageError("Package configuration could not be read.")

        if not self.verify():
            raise PackageError("Package configuration file is invalid.")

        self.name = self.conf.get("package", "name")

        modules_str = self.conf.get("package", "modules")
        abstract_module_list = modules_str.split(",")

        self.modules = OrderedDict()

        # TODO: this is beyond me at the moment, let's fix this later
        for module in abstract_module_list:
            abstract_module_type = PkgModuleType[module.upper()]                # FIXME
            concrete_module_type = PKG_MODULE_TYPE_DICT[abstract_module_type]   # FIXME
            mumbo = PKG_MODULE_DICT[abstract_module_type]                       # FIXME
            jumbo = self.modules[abstract_module_type]                          # FIXME

        # TODO: move writing state to after the action execution
        # ktr.state_write(conf_name, self.status())
        # ktr.state_write(conf_name, self.source.status())

    def status(self) -> dict:
        """
        This method returns statistics describing this Package object and its associated source.

        Returns:
            dict:   key-value pairs (property: value)
        """

        state = dict(package_name=self.name,
                     source_type=self.conf.get("source", "type"),
                     source_version=self.conf.get("source", "version"))
        return state

    def verify(self) -> bool:
        """
        This method verifies that the absolute minimum for proceeding with package initialisation is
        set. This also ensures the validity of some entries.

        Returns:
            bool:   *True* if configuration is minimally valid, *False* if entries are missing
        """

        assert isinstance(self.conf, ConfigParser)

        logger = KtrLogger(LOGPREFIX)

        success = True

        # [package]
        if "package" not in self.conf.sections():
            logger.err("Package configuration file does not have a 'package' section.")
            success = False

        # name =
        if "name" not in self.conf["package"]:
            logger.err("Package configuration file doesn't set 'name' in the 'package' section.")
            success = False

        if self.conf.get("package", "name") == "":
            logger.err("Package configuration file doesn't set 'name' in the 'package' section.")
            success = False

        # version =
        if "version" not in self.conf["package"]:
            logger.err("Package configuration file doesn't set 'version' in the 'package' section.")
            success = False

        if "-" in self.conf.get("package", "version"):
            logger.err("Hyphens are not a valid part of a version string.")
            logger.err("Replace it with another character, e.g. '~' or '+'.")
            success = False

        # modules =
        if self.conf.get("package", "modules") == "":
            logger.err("Package configuration file doesn't set 'modules' in the 'package' section.")
            success = False

        # [modules]
        if "modules" not in self.conf.sections():
            logger.err("Package configuration file does not have a 'modules' section.")
            success = False

        modules_str = self.conf.get("package", "modules")
        module_list = modules_str.split(",")

        for module in module_list:
            if module not in self.conf["modules"]:
                logger.err("Package configuration file doesn't define module " +
                           module +
                           "in the 'modules' section.")
                success = False

        # check for module configurations
        for module in module_list:
            if self.conf.get("modules", module) not in self.conf.sections():
                logger.err("Package configuration file doesn't have a section for module " +
                           module +
                           ".")
                success = False

        # TODO: delegate verifying all other config values to the appropriate places
        # but: verify only after class initialisation

        # if "constructor" in self.conf["package"]:
        #     success = success and self.constructor.verify()
        #
        # if "builder" in self.conf["package"]:
        #     success = success and self.builder.verify()
        #
        # if "uploader" in self.conf["package"]:
        #     success = success and self.uploader.verify()

        return success

    def update_config(self):
        """
        This method writes a changes package configuration back to the configuration file for
        permanent changes.
        """

        logger = KtrLogger(LOGPREFIX)

        try:
            conf_file = open(self.file, "w")
            self.conf.write(conf_file)
            conf_file.close()
        except OSError:
            logger.err("Package configuration file could not be written.")
            logger.err("Path: " + self.file)
            raise PackageError("Package configuration file could not be written.")
