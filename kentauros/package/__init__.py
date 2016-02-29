"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configparser import ConfigParser
import os

from kentauros.build import MockBuilder
from kentauros.config import KTR_CONF
from kentauros.construct import SrpmConstructor
from kentauros.definitions import KTR_SYSTEM_DATADIR, SourceType
from kentauros.init import err, log
from kentauros.source import SOURCE_TYPE_DICT
from kentauros.upload import CoprUploader


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
            src_type = self.conf['source']['type'].upper()

            self.source = SOURCE_TYPE_DICT[SourceType[src_type]](self)
            self.constructor = SrpmConstructor(self)
            self.builder = MockBuilder(self)
            self.uploader = CoprUploader(self)


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

