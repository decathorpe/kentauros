import abc
import configparser as cp
import os


# pylint: disable=too-many-ancestors
class FallbackConfiguration(cp.ConfigParser):
    def __init__(self):
        super().__init__()
        # TODO: Initialise with fallback values


class KtrContext(metaclass=abc.ABCMeta):
    """
    This class encapsulates information about the working directory, the kentauros project directory
    structure, and various runtime parameters, including whether debugging and/or warnings are
    enabled.

    Arguments:
        str basedir:                    base directory of the kentauros project

    Attributes:
        str basedir:                    base directory of the kentauros project
        str conf_path:                  path of the "kentaurosrc" configuration file
        cp.ConfigParser conf:           ConfigParser object holding the runtime configuration
        cp.ConfigParser conf_fallback:  ConfigParser object holding fallback configuration values
        bool debug:                     flag whether debugging is enabled or not
        bool warnings:                  flag whether warnings are enabled or not
    """

    def __init__(self, basedir: str):
        if not os.path.exists(basedir):
            raise FileNotFoundError(
                "The specified base directory ({}) could not be found.".format(basedir))

        self.basedir = basedir
        self.debug = bool()
        self.warnings = bool()

        conf_path = os.path.join(self.basedir, "kentaurosrc")
        if os.path.exists(conf_path):
            self.conf = cp.ConfigParser()
            self.conf.read(conf_path)

        self.conf_fallback = FallbackConfiguration()

    def get_basedir(self) -> str:
        """Returns the the base directory."""
        return self.basedir

    def get_confdir(self) -> str:
        """Returns the string "configs" appended to the base directory."""
        return os.path.join(self.get_basedir(), "configs")

    def get_datadir(self) -> str:
        """Returns the string "sources" appended to the base directory."""
        return os.path.join(self.get_basedir(), "sources")

    def get_expodir(self) -> str:
        """Returns the string "exports" appended to the base directory."""
        return os.path.join(self.get_basedir(), "exports")

    def get_packdir(self) -> str:
        """Returns the string "packages" appended to the base directory."""
        return os.path.join(self.get_basedir(), "packages")

    def get_specdir(self) -> str:
        """Returns the string "specs" appended to the base directory."""
        return os.path.join(self.get_basedir(), "specs")
