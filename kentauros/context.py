import abc
import os

from .config import KtrConfig
from .state import KtrState


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
    """

    def __init__(self, basedir: str, conf_path: str):
        assert isinstance(basedir, str)
        assert isinstance(conf_path, str)

        if not os.path.exists(basedir):
            raise FileNotFoundError(
                "The specified base directory ({}) could not be found.".format(basedir))

        if not os.path.exists(conf_path):
            raise FileNotFoundError(
                "The specified kentaurosrc file ({}) could not be found.".format(conf_path))

        self.basedir = basedir
        self.conf_path = conf_path

        self.state = KtrState(os.path.join(self.basedir, "state.json"))
        self.conf = KtrConfig(conf_path)

    @abc.abstractmethod
    def get_argument(self, key: str):
        """Returns an additional argument, for example the "force" flag."""

    @abc.abstractmethod
    def debug(self) -> bool:
        """Returns a boolean flag indicating enabled or disabled debugging messages."""

    @abc.abstractmethod
    def warnings(self) -> bool:
        """Returns a boolean flag indicating enabled or disabled warning messages."""

    @abc.abstractmethod
    def get_basedir(self) -> str:
        """Returns the the base directory."""

    @abc.abstractmethod
    def get_confdir(self) -> str:
        """Returns the directory containing package configuration files."""

    @abc.abstractmethod
    def get_datadir(self) -> str:
        """Returns the directory containing package sources."""

    @abc.abstractmethod
    def get_expodir(self) -> str:
        """Returns the directory containing built binary packages."""

    @abc.abstractmethod
    def get_packdir(self) -> str:
        """Returns the directory containing built source packages."""

    @abc.abstractmethod
    def get_specdir(self) -> str:
        """Returns the directory containing package specifications."""
