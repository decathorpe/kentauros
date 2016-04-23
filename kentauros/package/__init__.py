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
from kentauros.source.source import Source
from kentauros.upload import UPLOADER_TYPE_DICT, Uploader


LOGPREFIX1 = "ktr/package: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class PackageError(Exception):
    """
    This custom exception will be raised when errors occur during parsing of a
    package configuration file.

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
    This class envelops all things necessary to perform actions on a specific
    "package" of software.

    Arguments:
        str name:                   Base name of software package - reading
                                    $NAME.conf will be attempted for further
                                    information about the package.

    Attributes:
        ConfigParser conf:          parser for package.conf file
        Source source:              handling of upstream source code
        Constructor constructor:    handling of building compilable source
                                    packages
        Builder builder:            handling of building binary packages from
                                    source
        Uploader uploader:          handling of uploading source/binary packages
                                    to remote location

    Raises:
        PackageError:               error if package.conf file is invalid
    """

    def __init__(self, name: str):
        assert isinstance(name, str)

        self.name = name
        self.file = os.path.join(Kentauros().conf.confdir,
                                 self.name + ".conf")

        self.conf = ConfigParser()

        result = self.conf.read(self.file)
        if result == []:
            self.conf = None
            err(LOGPREFIX1 + "Package configuration could not be read.")
            err(LOGPREFIX1 + "Path: " + self.file)
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
        This method writes a changes package configuration back to the
        configuration file for permanent changes.
        """

        try:
            conf_file = open(self.file, "w")
            self.conf.write(conf_file)
            conf_file.close()
        except OSError:
            err(LOGPREFIX1 + "Package configuration file could not be written.")
            err(LOGPREFIX1 + "Path: " + self.file)

