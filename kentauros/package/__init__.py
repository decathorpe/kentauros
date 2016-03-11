"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configparser import ConfigParser, NoSectionError, NoOptionError
import os

from kentauros.init import err, log
from kentauros.config import ktr_get_conf
from kentauros.definitions import KTR_SYSTEM_DATADIR

from kentauros.definitions import BuilderType, ConstructorType
from kentauros.definitions import SourceType, UploaderType

from kentauros.build import BUILDER_TYPE_DICT, Builder
from kentauros.construct import CONSTRUCTOR_TYPE_DICT, Constructor
from kentauros.source import SOURCE_TYPE_DICT
from kentauros.source.common import Source
from kentauros.upload import UPLOADER_TYPE_DICT, Uploader


class PackageError(Exception):
    """
    kentauros.package.PackageError:
    exception class for package information parsing errors
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class Package:
    """
    kentauros.package.Package:
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(ktr_get_conf().confdir, self.name + ".conf")

        self.conf = ConfigParser()

        result = self.conf.read(self.file)
        if result == []:
            self.conf = None
            err("Package configuration could not be read.")
            err("Path: " + self.file)
            raise PackageError("Package configuration could not be read.")

        try:
            self.conf["package"]
        except KeyError:
            raise PackageError(
                "Package config file does not have a 'package' section.")

        try:
            self.conf["source"]
        except KeyError:
            raise PackageError(
                "Package config file does not have a 'source' section.")

        bld_type, con_type, src_type, upl_type = "", "", "", ""

        try:
            bld_type = str(self.conf.get("package", "builder")).upper()
        except NoOptionError:
            bld_type = "NONE"
        finally:
            if bld_type == "":
                bld_type = "NONE"

        try:
            con_type = str(self.conf.get("package", "constructor")).upper()
        except NoOptionError:
            con_type = "NONE"
        finally:
            if con_type == "":
                con_type = "NONE"

        try:
            src_type = str(self.conf.get("source", "type")).upper()
        except NoOptionError:
            src_type = "NONE"
        finally:
            if src_type == "":
                src_type = "NONE"

        try:
            upl_type = str(self.conf.get("package", "uploader")).upper()
        except NoOptionError:
            upl_type = "NONE"
        finally:
            if upl_type == "":
                upl_type = "NONE"

        # pylint: disable=unsubscriptable-object

        self.source = SOURCE_TYPE_DICT[
            SourceType[src_type]](self)
        self.constructor = CONSTRUCTOR_TYPE_DICT[
            ConstructorType[con_type]](self)
        self.builder = BUILDER_TYPE_DICT[
            BuilderType[bld_type]](self)
        self.uploader = UPLOADER_TYPE_DICT[
            UploaderType[upl_type]](self)


    def update_config(self):
        """
        kentauros.package.Package.update_config()
        method that writes package configuration out to $NAME.conf in CONFDIR
        """

        try:
            conf_file = open(self.file, "w")
            self.conf.write(conf_file)
            conf_file.close()
        except OSError:
            err("Package configuration file could not be written.")
            err("Path: " + self.file)

