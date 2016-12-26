"""
This sub-package contains the :py:class:`Package` class, which holds package configuration parsed
from the corresponding `package.conf` file. After parsing the package configuration, package
sub-modules are added according to configuration.
"""


import os

from collections import OrderedDict
from configparser import ConfigParser

from kentauros.definitions import PkgModuleType
from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.modules import PKG_MODULE_DICT, PKG_MODULE_TYPE_DICT
from kentauros.modules.module import PkgModule


LOG_PREFIX = "ktr/package"
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
        str file:                   configuration file path
        ConfigParser conf:          parser for package.conf file

    Raises:
        PackageError:               error if package.conf file is invalid
    """

    def __init__(self, conf_name: str):
        assert isinstance(conf_name, str)

        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        self.file = os.path.join(ktr.get_confdir(), conf_name + ".conf")
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

        modules_str = str(self.conf.get("package", "modules"))
        module_type_list = modules_str.split(",")

        if module_type_list == [""]:
            module_type_list = []

        self.modules = OrderedDict()

        for module_type in module_type_list:
            module_type_enum = PkgModuleType[module_type.upper()]
            module_implement = str(self.conf.get("modules", module_type)).upper()

            module = PKG_MODULE_DICT[module_type_enum][
                PKG_MODULE_TYPE_DICT[module_type_enum][module_implement]](self)

            self.modules[module_type] = module

        for module in self.modules.values():
            assert isinstance(module, PkgModule)
            module.verify()

    def get_module(self, module_type: str):
        """
        This method gets a specific package module from the module dictionary.

        Arguments:
            str module_type:    module type string (abstract class name, lower-case)

        Returns:
            PkgModule:          corresponding package module, if it is found
        """

        assert isinstance(module_type, str)

        try:
            return self.modules[module_type]
        except KeyError:
            return None

    def get_modules(self):
        """
        This method gets all a package's modules.

        Returns:
            list:       package module list
        """

        return self.modules.values()

    def get_conf_name(self) -> str:
        """
        Returns:
            str:    package configuration name
        """

        return self.conf_name

    def get_name(self) -> str:
        """
        Returns:
            str:    package name
        """

        return self.conf.get("package", "name")

    def get_version(self) -> str:
        """
        Returns:
            str:    package version string
        """

        return self.conf.get("package", "version")

    def replace_vars(self, input_str: str) -> str:
        """
        This method replaces variables in configuration file values with the appropriate values set
        elsewhere. For example, this can be used to specify the name and version inside a URL.

        Args:
            str input_str:  string where variables should be replaced

        Returns:
            str:            string where variables have been replaced
        """

        output_str = input_str

        if "%{name}" in output_str:
            output_str.replace("%{name}", self.get_name())

        if "%{version}" in output_str:
            output_str.replace("%{version}", self.get_version())

        return output_str

    def status(self) -> dict:
        """
        This method returns statistics describing this Package object and its associated source.

        Returns:
            dict:   key-value pairs (property: value)
        """

        state = dict(package_name=self.get_name(),
                     package_version=self.get_version())
        return state

    def status_string(self) -> str:
        """
        This method returns a string containing statistics describing this Package object and its
        associated source.

        Returns:
            str:    package information
        """

        string = ("Configuration:      {}\n".format(self.get_conf_name()) +
                  "-" * (len("Configuration:      ") + len(self.get_conf_name())) + "\n" +
                  "  Package name:     {}\n".format(self.get_name()) +
                  "  Package version:  {}\n".format(self.get_version()))

        return string

    def verify(self) -> bool:
        """
        This method verifies that the absolute minimum for proceeding with package initialisation is
        set. This also ensures the validity of some entries.

        Returns:
            bool:   *True* if configuration is minimally valid, *False* if entries are missing
        """

        assert isinstance(self.conf, ConfigParser)

        logger = KtrLogger(LOG_PREFIX)

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

        modules_str = str(self.conf.get("package", "modules"))
        module_list = modules_str.split(",")

        if module_list == [""]:
            module_list = []

        # check if the module is recognised
        for module in module_list:
            try:
                PkgModuleType[module.upper()]
            except KeyError:
                raise PackageError("Module '" + module + "' is not one of the recognised modules.")

        # check if modules are defined in the [modules] section
        for module in module_list:
            if module not in self.conf["modules"]:
                logger.err("Package configuration file doesn't define module '" +
                           module +
                           "' in the 'modules' section.")
                success = False

        # check if each module has its configuration section
        for module in module_list:
            if self.conf.get("modules", module) not in self.conf.sections():
                logger.err("Package configuration file doesn't have a section for module '" +
                           module +
                           "'.")
                success = False

        return success
