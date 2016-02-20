"""
kentauros.package module
base data structures containing information about and methods for packages
"""

import configparser
import os

from kentauros import KTR_SYSTEM_DATADIR

from kentauros.config import KTR_CONF
from kentauros.init import err, log


class Package(configparser.ConfigParser): # pylint: disable=too-many-ancestors
    """
    kentauros.package.Package:
    class that holds information about packages.
    at the moment, this only includes package name and the ConfigParser object
    """
    def __init__(self, name):
        super().__init__()
        self.file = os.path.join(KTR_CONF.confdir, name + ".conf")
        self.source = None

    def readin(self):
        """
        kentauros.package.Package.readin()
        method that reads package configuration from $NAME.conf file in CONFDIR
        """
        result = self.read(self.file)

        if result == []:
            err("Package configuration file could not be read.")
            err("Path: " + self.file)

        return False

    def writeout(self):
        """
        kentauros.package.Package.writeout()
        method that writes package configuration out to $NAME.conf in CONFDIR
        """

        try:
            self.write(self.file)
        except OSError:
            err("Package configuration file could not be written.")
            err("Path: " + self.file)

