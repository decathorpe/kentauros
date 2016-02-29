"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configparser import ConfigParser
import os

from kentauros.init import err, log
from kentauros.config import KTR_CONF
from kentauros.definitions import KTR_SYSTEM_DATADIR

from kentauros.definitions import BuilderType, ConstructorType, SourceType, UploaderType

from kentauros.build import BUILDER_TYPE_DICT
from kentauros.construct import CONSTRUCTOR_TYPE_DICT
from kentauros.source import SOURCE_TYPE_DICT
from kentauros.upload import UPLOADER_TYPE_DICT


class Package:
    """
    kentauros.package.Package:
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        self.name = name
        self.file = os.path.join(KTR_CONF['main']['confdir'], self.name + ".conf")

        self.conf = ConfigParser()

        result = self.conf.read(self.file)
        if result == []:
            self.conf = None
            err("Package configuration could not be read.")
            err("Path: " + self.file)

        else:
            # set source to Source subclass corresponding to setting in source/type
            bld_type = str("mock").upper()
            con_type = str("srpm").upper()
            src_type = str(self.conf.get("source", "type")).upper()
            upl_type = str("copr").upper()

            self.source = SOURCE_TYPE_DICT[SourceType[src_type]](self)
            self.constructor = CONSTRUCTOR_TYPE_DICT[ConstructorType[con_type]](self)
            self.builder = BUILDER_TYPE_DICT[BuilderType[bld_type]](self)
            self.uploader = UPLOADER_TYPE_DICT[UploaderType[upl_type]](self)


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

