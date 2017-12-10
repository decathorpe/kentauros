"""
This sub-package contains the :py:class:`Package` class, which holds package configuration parsed
from the corresponding `package.conf` file. After parsing the package configuration, package
sub-modules are added according to configuration.
"""

from collections import OrderedDict
from configparser import ConfigParser
import enum
import os
import warnings

from .definitions import PkgModuleType
from .instance import Kentauros
from .logcollector import LogCollector
from .modules import get_module, PkgModule
from .result import KtrResult


class PackageError(Exception):
    """
    This custom exception will be raised when errors occur during parsing of a package .conf file.

    Arguments:
        str value: informational string accompanying the exception
    """

    def __init__(self, value: str = ""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class ReleaseType(enum.Enum):
    STABLE = 0
    POST = 1
    PRE = 2


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

        self.file = os.path.join(ktr.get_confdir(), conf_name + ".conf")
        self.conf = ConfigParser(interpolation=None)
        self.conf_name = conf_name

        if not os.path.exists(self.file):
            raise FileNotFoundError("Package configuration file does not exist.")

        success = self.conf.read(self.file)
        if not success:
            raise PackageError("Package .conf file ({}) could not be read.".format(self.file))

        res = self.verify()
        if not res.success:
            warnings.warn("Log messages might be lost!", RuntimeWarning)
            res.messages.print()
            raise PackageError("Package configuration file is invalid.")

        self.name = self.conf.get("package", "name")

        modules_str = str(self.conf.get("package", "modules"))
        module_type_list = modules_str.split(",")

        if module_type_list == [""]:
            module_type_list = []

        self.modules = OrderedDict()

        for module_type in module_type_list:
            module_type_enum = PkgModuleType[module_type.upper()]
            module_implementer = str(self.conf.get("modules", module_type)).upper()

            module = get_module(module_type_enum, module_implementer, self)

            self.modules[module_type] = module

    def get_module(self, module_type: str) -> PkgModule:
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
        except KeyError as error:
            raise PackageError("No module found for type {}. Error: {}".format(str(module_type),
                                                                               repr(error)))

    def get_modules(self) -> list:
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

    def get_release_type(self) -> ReleaseType:
        return ReleaseType[self.conf.get("package", "release").upper()]

    def get_version_separator(self) -> str:
        release_type = self.get_release_type()

        ktr = Kentauros()

        separator_dict = dict()
        separator_dict[ReleaseType.STABLE] = ""
        separator_dict[ReleaseType.POST] = ktr.conf.get("main", "version_separator_post")
        separator_dict[ReleaseType.PRE] = ktr.conf.get("main", "version_separator_pre")

        return separator_dict[release_type]

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
            output_str = output_str.replace("%{name}", self.get_name())

        if "%{version}" in output_str:
            output_str = output_str.replace("%{version}", self.get_version())

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

    def verify(self) -> KtrResult:
        """
        This method verifies that the absolute minimum for proceeding with package initialisation is
        set. This also ensures the validity of some entries.

        Returns:
            bool:   *True* if configuration is minimally valid, *False* if entries are missing
        """

        assert isinstance(self.conf, ConfigParser)

        logger = LogCollector("Package {}".format(self.conf_name))

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

        # release =
        if "release" not in self.conf["package"]:
            logger.log("Package configuration type doesn't specify release type.")
        elif self.conf.get("package", "release") not in ["stable", "pre", "post"]:
            logger.log("Package release type not supported ({} is not in [stable, post, pre])."
                       .format(self.conf.get("package", "release")))
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

        return KtrResult(success, logger)
