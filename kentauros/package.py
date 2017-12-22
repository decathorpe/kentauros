"""
This sub-package contains the the :py:class:`Package` class, which encapsulates information about a
package (as the name suggests), as defined by the package's `.conf` configuration file.
"""

import enum
import os

from .config import KtrConfig
from .context import KtrContext
from .result import KtrResult
from .validator import KtrValidator


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
    """
    This enum determines the type of release that will be packaged - either a stable release, a
    pre-release snapshot, or a post-release snapshot.
    """

    STABLE = 0
    POST = 1
    PRE = 2


class KtrPackage:
    """
    Arguments:
        str conf_path:  path to the package configuration file (relative or absolute)

    Attributes:
        str conf_path:      path to the package configuration file (relative or absolute)
        str conf_name:      name of the package configuration (path basename stripped of ".conf")
        ConfigParser conf:  ConfigParser object holding the package configuration information
    """

    def __init__(self, context: KtrContext, conf_name: str):
        assert isinstance(context, KtrContext)
        assert isinstance(conf_name, str)

        self.context = context

        self.conf_name = conf_name
        self.conf_path = os.path.join(self.context.get_confdir(), self.conf_name + ".conf")
        self.conf = KtrConfig(self.conf_path)
        self.name = self.conf.get("package", "name")

    def get_version(self) -> str:
        """
        Returns:
            str:    package version string
        """

        return self.conf.get("package", "version")

    def get_release_type(self) -> ReleaseType:
        """
        Returns:
             ReleaseType:   release type enum
        """

        return ReleaseType[self.conf.get("package", "release").upper()]

    def get_version_separator(self) -> str:
        """
        Returns:
            str:    version separator, depending on release type
        """

        release_type = self.get_release_type()

        separator_dict = dict()
        separator_dict[ReleaseType.STABLE] = ""
        separator_dict[ReleaseType.POST] = self.context.conf.get("main", "version_separator_post")
        separator_dict[ReleaseType.PRE] = self.context.conf.get("main", "version_separator_pre")

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
            output_str = output_str.replace("%{name}", self.name)

        if "%{version}" in output_str:
            output_str = output_str.replace("%{version}", self.get_version())

        return output_str

    def status(self) -> KtrResult:
        """
        This method returns statistics describing this Package object and its associated source.

        Returns:
            dict:   key-value pairs (property: value)
        """

        state = dict(package_name=self.name,
                     package_version=self.get_version())

        return KtrResult(True, state=state)

    def status_string(self) -> KtrResult:
        """
        This method returns a string containing statistics describing this Package object and its
        associated source.

        Returns:
            str:    package information
        """

        template = """
        Configuration:      {conf_name}
        ------------------------------------------------------------
          Package name:     {name}
          Package version:  {version}
          Release type:     {release_type}
        """

        string = template.format(conf_name=self.conf_name,
                                 name=self.name,
                                 version=self.get_version(),
                                 release_type=str(self.get_release_type()))

        return KtrResult(True, string)

    def verify(self) -> KtrResult:
        name = "Package {}".format(self.conf_name)
        ret = KtrResult(True, name=name)

        conf = self.conf.conf

        # check [package] section
        package_expected_keys = ["name", "version", "release", "modules"]

        package_validator = KtrValidator(conf, "package", package_expected_keys)
        res = package_validator.validate()
        ret.collect(res)

        # check validity of [package][release] option ("stable", "post", or "pre")
        if conf.has_section("package") and conf.has_option("package", "release"):
            ret.success = ret.success and (
                conf.get("package", "release") in ["stable", "post", "pre"])

        # check [modules] section, if present
        if conf.has_section("package") and conf.has_option("package", "modules"):
            modules: str = conf.get("package", "modules")

            if modules == "":
                modules_expected_keys = []
            else:
                modules_expected_keys = modules.split(",")

            modules_validator = KtrValidator(conf, "modules", modules_expected_keys)
            res = modules_validator.validate()
            ret.collect(res)

            # check if sections for all modules exist
            modules = modules_expected_keys

            for module in modules:
                if not conf.has_section(module):
                    ret.success = False

        return ret
