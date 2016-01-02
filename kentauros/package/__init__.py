"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configparser import ConfigParser
import os

from kentauros.base import err
from kentauros.init import BASEDIR, CONFDIR, DATADIR


class Package:
    """
    kentauros.package.Package
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        self.name = name
        self.conf = None

    def readin(self):
        """
        kentauros.package.Package.readin()
        method that reads package configuration from $NAME.conf file in CONFDIR
        """
        self.conf = ConfigParser()
        try:
            self.conf.read(os.path.join(CONFDIR, self.name + ".conf"))
        except OSError:
            err("Package configuration file for " + self.name + " could not be read.")
            self.conf = None

    def writeout(self):
        """
        kentauros.package.Package.writeout()
        method that writes package configuration out to $NAME.conf in CONFDIR
        """
        if self.conf is None:
            err("Package configuration is not present and cannot be written to file.")
        try:
            self.conf.write(os.path.join(CONFDIR, self.name + ".conf"))
        except OSError:
            err("Package configuration file for " + self.name + " could not be written.")

