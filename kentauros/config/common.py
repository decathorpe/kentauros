"""
# TODO: napoleon module docstring
kentauros.config.common
this file contains common functions, definitions, classes and methods for
all configuration methods.
"""


from configparser import ConfigParser, NoOptionError
import os

from kentauros.definitions import KtrConfType
from kentauros.init.env import get_env_debug


LOGPREFIX1 = "ktr/config/common: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""
LOGPREFIX2 = "                   - "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


class ConfigException(Exception):
    """
    # TODO: napoleon class docstring
    kentauros.config.common.ConfigException:
    exception that is raised if erors occur during configuration parsing
    """
    def __init__(self, value):
        super().__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


def __replace_home__(string):
    if string is None:
        return None

    home = os.environ.get("HOME")

    if "$HOME" in string:
        return string.replace("$HOME", home)
    elif "~" in string:
        return string.replace("~", home)
    else:
        return string


class KtrConf:
    """
    # TODO: napoleon class docstring
    kentauros.config.common.KtrConf
    class that contains information about kentauros configuration options.
    this includes:
    - location of base directory (basedir)
    - location of package configuration files (confdir)
    - location of package source directories / tarballs (datadir)
    - location of built source packages (packdir)
    - location of package spec files (specdir)
    - may be extended
    """
    def __init__(self, conftype, basedir=None):
        assert isinstance(conftype, KtrConfType)

        if basedir is None:
            self.basedir = None
            self.confdir = None
            self.datadir = None
            self.packdir = None
            self.specdir = None

        else:
            self.basedir = basedir
            self.confdir = os.path.join(self.basedir, "configs")
            self.datadir = os.path.join(self.basedir, "sources")
            self.packdir = os.path.join(self.basedir, "packages")
            self.specdir = os.path.join(self.basedir, "specs")

        self.type = conftype

        # if values are read from config file, remember where from
        self.file = None
        self.conf = None


    def validate(self):
        """
        # TODO: napoleon method docstring
        kentauros.config.base.KtrConf.validate()
        method for verifying valid configuration content.
        """
        # basedir does not have to be checked, because:
        # - it is either set at initialisation and
        #   defines all other values, or
        # - it is not set at initialisation and
        #   all other values have been defined manually
        if (self.confdir is None) or \
           (self.datadir is None) or \
           (self.packdir is None) or \
           (self.specdir is None):
            return False
        else:
            return True


    def succby(self, other):
        """
        # TODO: napoleon method docstring
        kentauros.config.common.KtrConf.succby()
        method that replaces config values in this KtrConf (self) with non-None
        config values from another KtrConf (other)
        """
        assert isinstance(other, KtrConf)

        # if basedir is not set: all other values have been explicitly set,
        # so override all of them
        if other.validate():
            self.basedir = __replace_home__(other.basedir)
            self.confdir = other.confdir
            self.datadir = other.datadir
            self.packdir = other.packdir
            self.specdir = other.specdir

        if not self.validate():
            print(LOGPREFIX1 + \
                "Last attempted action was overriding default values.")
            raise ConfigException("Error occured during configuration parsing.")


    def from_file(self, filepath, errmsg=None):
        """
        # TODO: napoleon method docstring
        kentauros.config.common.KtrConf.from_file():
        method that reads a configuration file and parses read values into
        object attributes
        """

        if not os.path.exists(filepath):
            if get_env_debug():
                print(LOGPREFIX1 + errmsg)
            return None

        self.file = filepath
        self.conf = ConfigParser()

        successful = self.conf.read(self.file)
        if not successful:
            if errmsg:
                print(LOGPREFIX1 + errmsg)
            return None

        if "main" not in self.conf.sections():
            return None

        try:
            self.basedir = os.path.abspath(
                __replace_home__(self.conf.get("main", "basedir")))
        except NoOptionError:
            self.basedir = None
        finally:
            if self.basedir == "":
                self.basedir = None

        if "confdir" in self.conf.options("main"):
            self.confdir = os.path.abspath(
                __replace_home__(self.conf.get("main", "confdir")))
        else:
            self.confdir = os.path.join(self.basedir, "configs")

        if "datadir" in self.conf.options("main"):
            self.datadir = os.path.abspath(
                __replace_home__(self.conf.get("main", "datadir")))
        else:
            self.datadir = os.path.join(self.basedir, "sources")

        if "packdir" in self.conf.options("main"):
            self.packdir = os.path.abspath(
                __replace_home__(self.conf.get("main", "packdir")))
        else:
            self.packdir = os.path.join(self.basedir, "packages")

        if "specdir" in self.conf.options("main"):
            self.specdir = os.path.abspath(
                __replace_home__(self.conf.get("main", "specdir")))
        else:
            self.specdir = os.path.join(self.basedir, "specs")

        if not self.validate():
            print(LOGPREFIX1 + \
                "Not all neccessary configuration options have been set.")
            print(LOGPREFIX2 + self.file)
            return None
        else:
            return self

