"""
This subpackage contains the :py:class:`Package` class, which holds package configuration parsed
from the corresponding `package.conf` file (errors that occur during parsing are probably not
handled correctly yet). After parsing the package configuration, :py:class:`Source`,
:py:class:`Constructor`, :py:class:`Builder` and :py:class:`Uploader` instances are set as
attributes according to configuration.
"""


from configparser import ConfigParser
import os

from kentauros.definitions import BuilderType, ConstructorType, SourceType, UploaderType

from kentauros.instance import Kentauros

from kentauros.build import BUILDER_TYPE_DICT
from kentauros.construct import CONSTRUCTOR_TYPE_DICT
from kentauros.sources import SOURCE_TYPE_DICT
from kentauros.upload import UPLOADER_TYPE_DICT


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

        ktr = Kentauros(LOGPREFIX)

        self.file = os.path.join(ktr.conf.get_confdir(), conf_name + ".conf")
        self.conf = ConfigParser()
        self.conf_name = conf_name

        if not os.path.exists(self.file):
            raise FileNotFoundError("Package configuration file does not exist.")

        success = self.conf.read(self.file)
        if not success:
            ktr.err("Package configuration could not be read.")
            ktr.err("Path: " + self.file)
            raise PackageError("Package configuration could not be read.")

        if not self.verify():
            raise PackageError("Package configuration file is invalid.")

        self.name = self.conf.get("package", "name")

        self.source = self._get_source()
        self.constructor = self._get_constructor()
        self.builder = self._get_builder()
        self.uploader = self._get_uploader()

        ktr.state_write(conf_name, self.status())
        ktr.state_write(conf_name, self.source.status())

    def _get_builder(self):
        """
        This method tries to get a :py:class:`Builder` instance corresponding to the values set in
        the package configuration.

        Returns:
            Builder:    package builder object
        """

        if "builder" not in self.conf["package"]:
            raise PackageError("No builder has been specified in the configuration file.")
        else:
            builder_type = str(self.conf.get("package", "builder")).upper()
            try:
                builder = BUILDER_TYPE_DICT[BuilderType[builder_type]](self)
            except KeyError:
                raise PackageError("The specified builder type is not supported.")
            return builder

    def _get_constructor(self):
        """
        This method tries to get a :py:class:`Constructor` instance corresponding to the values set
        in the package configuration.

        Returns:
            Constructor:    package constructor object
        """

        if "constructor" not in self.conf["package"]:
            raise PackageError("No constrctor has been specified in the configuration file.")
        else:
            constructor_type = str(self.conf.get("package", "constructor")).upper()
            try:
                constructor = CONSTRUCTOR_TYPE_DICT[ConstructorType[constructor_type]](self)
            except KeyError:
                raise PackageError("The specified constructor type is not supported.")
            return constructor

    def _get_source(self):
        """
        This method tries to get a :py:class:`Source` instance corresponding to the values set in
        the package configuration.

        Returns:
            Source: package source object
        """

        source_type = str(self.conf.get("source", "type")).upper()
        try:
            source = SOURCE_TYPE_DICT[SourceType[source_type]](self)
        except KeyError:
            raise PackageError("The specified source type is not supported.")
        return source

    def _get_uploader(self):
        """
        This method tries to get a :py:class:`Uploader` instance corresponding to the values set in
        the package configuration.

        Returns:
            Uploader:   package uploader object
        """

        if "uploader" not in self.conf["package"]:
            raise PackageError("No uploader has been specified in the configuration file.")
        else:
            uploader_type = str(self.conf.get("package", "uploader")).upper()
            try:
                uploader = UPLOADER_TYPE_DICT[UploaderType[uploader_type]](self)
            except KeyError:
                raise PackageError("The specified uploader type is not supported.")
            return uploader

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

        ktr = Kentauros(LOGPREFIX)

        success = True

        if "package" not in self.conf.sections():
            ktr.err("Package configuration file does not have a 'package' section.")
            success = False

        if "source" not in self.conf.sections():
            ktr.err("Package configuration file does not have a 'source' section.")
            success = False

        if "type" not in self.conf["source"]:
            ktr.err("Package configuration file does not specify the type of source.")
            success = False

        if self.conf.get("source", "type") == "":
            ktr.err("Package configuration file does not specify the type of source.")
            success = False

        if "version" not in self.conf["source"]:
            ktr.err("Package configuration file does not specify the source version.")
            success = False

        if self.conf.get("source", "version") == "":
            ktr.err("Package configuration file does not specify the source version.")
            success = False

        if "-" in self.conf.get("source", "version"):
            ktr.err("Hyphens are not a valid part of a version string.")
            ktr.err("Replace it with another character, e.g. '~' or '+'.")
            success = False

        # TODO: delegate verifying all other config values to the appropriate places

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

        ktr = Kentauros(LOGPREFIX)

        try:
            conf_file = open(self.file, "w")
            self.conf.write(conf_file)
            conf_file.close()
        except OSError:
            ktr.err("Package configuration file could not be written.")
            ktr.err("Path: " + self.file)
            raise PackageError("Package configuration file could not be written.")
