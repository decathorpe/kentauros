"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configobj import ConfigObj
import os
from validate import Validator

from kentauros.config import KTR_CONF
from kentauros.init import err, log


SPECFILE = "/usr/share/kentauros/package_verifyspec.conf"
CONFIGSPEC = ConfigObj(SPECFILE, list_values=False)


class Package:
    """
    kentauros.package.Package
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        self.name = name
        self.conf = None
        self.file = os.path.join(KTR_CONF.confdir,
                                 self.name + ".conf")

    def readin(self):
        """
        kentauros.package.Package.readin()
        method that reads package configuration from $NAME.conf file in CONFDIR
        """
        try:
            self.conf = ConfigObj(self.file,
                                  write_empty_values=True,
                                  configspec=CONFIGSPEC)
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
            self.conf.write()
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

        val = Validator()
        test = self.conf.validate(val)
        return test

    def create(self):
        """
        kentauros.package.Package.validate()
        method that creates a new config file with default or empty values
        """

        val = Validator()

        self.conf = ConfigObj(self.file, configspec=CONFIGSPEC)
        test = self.conf.validate(val, copy=True)

        log("Dummy package configuration written successfully.", 2)
        return test

