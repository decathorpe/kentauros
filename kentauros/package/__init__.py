"""
kentauros.package module
base data structures containing information about and methods for packages
"""

import configparser
import os

from kentauros import KTR_SYSTEM_DATADIR

from kentauros.config import KTR_CONF
from kentauros.init import err, log


PKG_DEFAULT_CONF_FILE = os.path.join(KTR_SYSTEM_DATADIR, "package.conf")


class Package:
    """
    kentauros.package.Package
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        self.name = name
        self.conf = None
        self.file = os.path.join(KTR_CONF.confdir, self.name + ".conf")

    def readin(self):
        """
        kentauros.package.Package.readin()
        method that reads package configuration from $NAME.conf file in CONFDIR
        """
        try:
            self.conf = configparser.ConfigParser()
            self.conf.read(self.file)
        except OSError:
            err("Package configuration file for " +
                self.name +
                " could not be read.")
            err("Path: " + self.file)
            self.conf = None

    def writeout(self):
        """
        kentauros.package.Package.writeout()
        method that writes package configuration out to $NAME.conf in CONFDIR
        """
        if self.conf is None:
            err("Package configuration is not present and cannot be written to file.")

        try:
            self.conf.write(self.file)
        except OSError:
            err("Package configuration file for " +
                self.name +
                " could not be written.")
            err("Path: " + self.file)

    def validate(self):
        """
        kentauros.package.Package.validate()
        method that validates that every expected config value is present
        """
        pass

