"""
This module contains the :py:class:`KtrConf` class and helper things.
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
    This custom exception will be raised when errors occur during parsing of a
    kentauros configuration file.

    Arguments:
        str value: informational string accompanying the exception
    """

    def __init__(self, value: str):
        super().__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


def __replace_home__(string: str) -> str:
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
    This class is used to get and store kentauros configuration from one of the
    valid sources.

    Valid configuration file locations include (in ascending priority):

    - system-wide default configuration, installed with kentauros:
      `/usr/share/kentauros/default.conf`
    - system-wide custom configuration, created by the user:
      `/etc/kentaurosrc`
    - user-wide configuration: `$HOME/.config/kentaurosrc`
    - project-specific configuration: `./kentaurosrc`
    - environment variables: `KTR_BASEDIR`, `KTR_CONFDIR`, etc.
    - command-line switches: `--basedir=BASEDIR`, etc.

    The settings stored in attributes of this class include:

    - location of kentauros base directory (`basedir`)
    - location of package configuration directory (`confdir`)
    - location of package source directories (`datadir`)
    - location of package specification directory (`specdir`)
    - location of directory containing built packages (`packdir`)

    Arguments:
        KtrConfType conftype:   type of this configuration (where it was read
                                from)
        str basedir:            optional string specifying `basedir` at class
                                initialisation
    """

    def __init__(self, conftype: KtrConfType, basedir: str=None):
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


    def validate(self) -> bool:
        """
        This method contains a simple and stupid, fast verification that the
        stored configuration does not contain missing values (`None`).

        Returns:
            bool: `True` if a basic test is passed, `False` if not
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
        This method overrides attributes with those from another
        :py:class:`KtrConf` instance and does basic verification of the
        resulting configuration values.

        Arguments:
            KtrConf other:      configuration from which values are read

        Raises:
            ConfigException:    This exception is raised when an error occurs
                                during configuration verification.
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
            self.type = other.type

        if not self.validate():
            print(LOGPREFIX1 + \
                "Last attempted action was overriding default values.", flush=True)
            raise ConfigException("Error occured during configuration parsing.")


    def from_file(self, filepath: str, errmsg: str=None):
        """
        This method is used to read values from an `ini`-style configuration
        file and store the results in the instance's attributes.

        It also stores the :py:class:`ConfigParser` object and file path, in
        case they were needed along the line.

        Arguments:
            str filepath:   path to configuration file
            str errmsg:     error message that will be printed in case the file
                            is not found at the specified location

        Returns:
            KtrConf:        returns instance itself for prettier code later on,\
                            or `None` if file is not found.
        """

        if not os.path.exists(filepath):
            if get_env_debug():
                print(LOGPREFIX1 + errmsg, flush=True)
            return None

        self.file = filepath
        self.conf = ConfigParser()

        successful = self.conf.read(self.file)
        if not successful:
            if errmsg:
                print(LOGPREFIX1 + errmsg, flush=True)
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
                "Not all neccessary configuration options have been set.", flush=True)
            print(LOGPREFIX2 + self.file, flush=True)
            return None
        else:
            return self

