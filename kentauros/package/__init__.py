"""
kentauros.package module
base data structures containing information about and methods for packages
"""

from configparser import ConfigParser

from kentauros.init import BASEDIR

def get_configpath(name, basedir):
    return os.path.join(basedir, "configs", name + ".conf")

class Package:
    def __init__(self, name):
        self.name = name
        self.conf = None

    def readin(self):
        self.conf = ConfigParser()
        try:
            self.conf.read(get_configpath(name, BASEDIR))
        except OSError:
            err("Package configuration file for " + name + " could not be read.")
            self.conf = None

    def writeout(self):
        if self.conf is None:
            err("Package configuration is not present and cannot be written to file.")
        try:
            self.conf.write(get_configpath(name, BASEDIR))
        except OSError:
            err("Package configuration file for " + name + " could not be written.")

