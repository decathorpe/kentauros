"""
This subpackage contains the :py:class:`Package` class, which holds package configuration parsed
from the corresponding `package.conf` file (errors that occur during parsing are probably not
handled correctly yet). After parsing the package configuration, :py:class:`Source`,
:py:class:`Constructor`, :py:class:`Builder` and :py:class:`Uploader` instances are set as
attributes according to configuration.
"""


# TODO: rework ktr/package submodule


from configparser import ConfigParser
import os

from kentauros.definitions import BuilderType, ConstructorType, SourceType, UploaderType

from kentauros.instance import Kentauros

from kentauros.build import BUILDER_TYPE_DICT
from kentauros.construct import CONSTRUCTOR_TYPE_DICT
from kentauros.sources import SOURCE_TYPE_DICT
from kentauros.upload import UPLOADER_TYPE_DICT


LOGPREFIX1 = "ktr/package: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
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
        str name:                   Base name of software package - reading $NAME.conf will be
                                    attempted for further information about the package.

    Attributes:
        ConfigParser conf:          parser for package.conf file
        Source source:              handling of upstream source code
        Constructor constructor:    handling of building compilable source packages
        Builder builder:            handling of building binary packages from source
        Uploader uploader:          handling of uploading source/binary packages to remote location

    Raises:
        PackageError:               error if package.conf file is invalid
    """

    def __init__(self, name: str):
        assert isinstance(name, str)

        ktr = Kentauros(LOGPREFIX1)

        self.file = os.path.join(ktr.conf.get_confdir(), name + ".conf")
        self.conf = ConfigParser()

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

        if "builder" not in self.conf["package"]:
            # self.build = lambda *args: None
            raise PackageError("No builder has been specified in the configuration file.")
        else:
            bld_type = str(self.conf.get("package", "builder")).upper()
            try:
                self.builder = BUILDER_TYPE_DICT[BuilderType[bld_type]](self)
                # self.build = BUILDER_TYPE_DICT[BuilderType[bld_type]](self).build
            except KeyError:
                raise PackageError("The specified builder type is not supported.")

        if "constructor" not in self.conf["package"]:
            # self.construct = lambda *args: None
            raise PackageError("No constrctor has been specified in the configuration file.")
        else:
            con_type = str(self.conf.get("package", "constructor")).upper()
            try:
                self.constructor = CONSTRUCTOR_TYPE_DICT[ConstructorType[con_type]](self)
                # self.construct = CONSTRUCTOR_TYPE_DICT[ConstructorType[con_type]](self).construct
            except KeyError:
                raise PackageError("The specified constructor type is not supported.")

        src_type = str(self.conf.get("source", "type")).upper()
        try:
            self.source = SOURCE_TYPE_DICT[SourceType[src_type]](self)
            # self.upstream_source = SOURCE_TYPE_DICT[SourceType[src_type]](self).source
        except KeyError:
            raise PackageError("The specified source type is not supported.")

        if "uploader" not in self.conf["package"]:
            # self.upload = lambda *args: None
            raise PackageError("No uploader has been specified in the configuration file.")
        else:
            upl_type = str(self.conf.get("package", "uploader")).upper()
            try:
                self.uploader = UPLOADER_TYPE_DICT[UploaderType[upl_type]](self)
                # self.upload = UPLOADER_TYPE_DICT[UploaderType[upl_type]](self).upload
            except KeyError:
                raise PackageError("The specified uploader type is not supported.")

    def verify(self) -> bool:
        """
        This method verifies that the absolute minimum for proceeding with package initialisation
        is set.

        Returns:
            bool:   *True* if configuration is minimally valid, *False* if entries are missing
        """

        assert isinstance(self.conf, ConfigParser)

        ktr = Kentauros(LOGPREFIX1)

        if "package" not in self.conf.sections():
            ktr.err("Package configuration file does not have a 'package' section.")
            return False

        if "source" not in self.conf.sections():
            ktr.err("Package configuration file does not have a 'source' section.")
            return False

        if "type" not in self.conf["source"]:
            ktr.err("Package configuration file does not specify the type of source.")
            return False

        return True

    def update_config(self):
        """
        This method writes a changes package configuration back to the
        configuration file for permanent changes.
        """

        ktr = Kentauros(LOGPREFIX1)

        try:
            conf_file = open(self.file, "w")
            self.conf.write(conf_file)
            conf_file.close()
        except OSError:
            ktr.err("Package configuration file could not be written.")
            ktr.err("Path: " + self.file)
