"""
This subpackage contains the :py:class:`Package` class, which holds package
configuration parsed from the corresponding `package.conf` file (errors that
occur during parsing are probably not handled correctly yet). After parsing the
package configuration, :py:class:`Source`, :py:class:`Constructor`,
:py:class:`Builder` and :py:class:`Uploader` instances are set as attributes
according to configuration.
"""

from configparser import ConfigParser, NoSectionError, NoOptionError
import os

from kentauros.definitions import KTR_SYSTEM_DATADIR
from kentauros.definitions import BuilderType, ConstructorType
from kentauros.definitions import SourceType, UploaderType

from kentauros.instance import Kentauros, err, log

from kentauros.build import BUILDER_TYPE_DICT, Builder
from kentauros.construct import CONSTRUCTOR_TYPE_DICT, Constructor
from kentauros.source import SOURCE_TYPE_DICT
from kentauros.source.common import Source
from kentauros.upload import UPLOADER_TYPE_DICT, Uploader


LOGPREFIX1 = "ktr/package: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class PackageError(Exception):
    """
    # TODO: napoleon class docstring
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
    # TODO: napoleon class docstring
    kentauros.package.Package:
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(Kentauros().conf.confdir,
                                 self.name + ".conf")

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
        # TODO: napoleon method docstring
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

