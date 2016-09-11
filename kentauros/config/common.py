"""
This module contains the :py:class:`KtrConf` class and helper things.
"""


from configparser import ConfigParser, NoOptionError
import os

from kentauros.definitions import KtrConfType
from kentauros.init.env import get_env_debug


LOGPREFIX1 = "ktr/config/common: "
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""

LOGPREFIX2 = "                   - "
"""This string specifies the prefix for lists printed through log and error functions, printed to
stdout or stderr from inside this subpackage.
"""


class ConfigException(Exception):
    """
    This custom exception will be raised when errors occur during parsing of a kentauros
    configuration file.

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
    elif "$(HOME)" in string:
        return string.replace("$(HOME)", home)
    elif "~" in string:
        return string.replace("~", home)
    else:
        return string


class KtrConf:
    """
    This class is used to get and store kentauros configuration from one of the valid sources.

    Valid configuration file locations include (in ascending priority):

    - system-wide default configuration, installed with kentauros:
      `/usr/share/kentauros/default.conf`
    - system-wide custom configuration, created by the user: `/etc/kentaurosrc`
    - user-wide configuration: `$HOME/.config/kentaurosrc`
    - project-specific configuration: `./kentaurosrc`
    - environment variables: `KTR_BASEDIR`
    - command-line switches: `--basedir=BASEDIR`

    At the moment, the settings stored in attributes of this class include:

    - the location of kentauros base directory (`basedir`)

    Arguments:
        KtrConfType conftype:   type of this configuration (where it was read from)
        str basedir:            optional string specifying `basedir`
    """

    def __init__(self, conftype: KtrConfType, basedir: str=None):
        assert isinstance(conftype, KtrConfType)

        if basedir is None:
            self.basedir = None
        else:
            self.basedir = os.path.abspath(__replace_home__(basedir))

        self.type = conftype

        # if values are read from config file, remember where from
        self.file = None
        self.conf = None

    def get_basedir(self):
        """
        This method returns the kentauros basedir.

        Returns:
            str:    base directory
        """
        return self.basedir

    def get_confdir(self):
        """
        This method returns the kentauros directory for config files.

        Returns:
            str:    config directory
        """

        if self.basedir is None:
            return None
        else:
            return os.path.join(self.basedir, "configs")

    def get_datadir(self):
        """
        This method returns the kentauros directory for sources.

        Returns:
            str:    source directory
        """

        if self.basedir is None:
            return None
        else:
            return os.path.join(self.basedir, "sources")

    def get_expodir(self):
        """
        This method returns the kentauros directory for built binary packages.

        Returns:
            str:    binary package directory
        """

        if self.basedir is None:
            return None
        else:
            return os.path.join(self.basedir, "exports")

    def get_packdir(self):
        """
        This method returns the kentauros directory for source packages.

        Returns:
            str:    source package directory
        """

        if self.basedir is None:
            return None
        else:
            return os.path.join(self.basedir, "packages")

    def get_specdir(self):
        """
        This method returns the kentauros directory for package specs.

        Returns:
            str:    package spec directory
        """

        if self.basedir is None:
            return None
        else:
            return os.path.join(self.basedir, "specs")

    def validate(self) -> bool:
        """
        This method contains a simple and stupid, fast verification that the stored configuration
        does not contain missing values (`None`).

        Returns:
            bool: `True` if a basic test is passed, `False` if not
        """

        if self.get_basedir() is None:
            return False

        if (self.get_confdir() is None) or \
           (self.get_datadir() is None) or \
           (self.get_packdir() is None) or \
           (self.get_specdir() is None):
            return False
        else:
            return True

    def succby(self, other):
        """
        This method overrides attributes with those from another :py:class:`KtrConf` instance and
        does basic verification of the resulting configuration values.

        Arguments:
            KtrConf other:      configuration from which values are read

        Raises:
            ConfigException:    raised when an error occurs during config verification
        """

        assert isinstance(other, KtrConf)

        if other.validate():
            self.basedir = other.basedir
            self.type = other.type

        if not self.validate():
            raise ConfigException("Error occured during configuration parsing.")

    def from_file(self, filepath: str, errmsg: str=None):
        """
        This method is used to read values from an `ini`-style configuration file and store the
        results in the instance's attributes.

        It also stores the :py:class:`ConfigParser` object and file path, in case they were needed
        along the line.

        Arguments:
            str filepath:   path to configuration file
            str errmsg:     error message that will be printed in case the file is not found

        Returns:
            KtrConf:        returns instance itself or *None* if file is not found.
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
            self.basedir = os.path.abspath(__replace_home__(self.conf.get("main", "basedir")))
        except NoOptionError:
            self.basedir = None
        finally:
            if self.basedir == "":
                self.basedir = None

        if not self.validate():
            print(LOGPREFIX1 + "Not all neccessary configuration options have been set.")
            print(LOGPREFIX2 + self.file)
            return None
        else:
            return self


def ktr_conf_from_file(conftype: KtrConfType, filepath: str, errmsg: str=None) -> KtrConf:
    """
    This factory method is used to create a :py:class:`KtrConf` instance with values that are read
    from an `ini`-style configuration file and store the results in the instance's attributes.

    It also stores the :py:class:`ConfigParser` object and file path, in
    case they are needed later.

    Arguments:
        KtrConfType conftype:   type of configuration
        str filepath:           path to configuration file
        str errmsg:             error message that will be printed in case the file is not found

    Returns:
        KtrConf:                resulting configuration object
    """

    if not os.path.exists(filepath):
        if get_env_debug():
            print(LOGPREFIX1 + errmsg)
        return None

    config = ConfigParser()

    successful = config.read(filepath)
    if not successful:
        if errmsg:
            print(LOGPREFIX1 + errmsg)
            return None

    if "main" not in config.sections():
        print(LOGPREFIX1 + "Configuration file invalid (no 'main' section).")
        print(LOGPREFIX2 + filepath)
        return None

    basedir = None

    try:
        basedir = config.get("main", "basedir")
    except NoOptionError:
        return None
    finally:
        if basedir == "":
            basedir = None

    result = KtrConf(conftype=conftype, basedir=basedir)

    if not result.validate():
        print(LOGPREFIX1 + "Something went wrong during configuration verification.")
        return None
    else:
        return result
