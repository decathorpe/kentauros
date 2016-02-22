"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configparser import ConfigParser
import os

from kentauros import KTR_SYSTEM_DATADIR

from kentauros.build import MockBuilder
from kentauros.config import KTR_CONF
from kentauros.construct import SrpmConstructor
from kentauros.init import err, log
from kentauros.source import SourceType, SOURCE_TYPE_DICT


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
            self.source = SOURCE_TYPE_DICT[SourceType[src_type]](self.conf)
            self.constructor = SrpmConstructor(self)
            self.builder = MockBuilder(self)
            #self.uploader = CoprUploader(self.conf)


    def conf_write(self):
        """
        kentauros.package.Package.writeout()
        method that writes package configuration out to $NAME.conf in CONFDIR
        """

        try:
            self.conf.write(self.file)
        except OSError:
            err("Package configuration file could not be written.")
            err("Path: " + self.file)

