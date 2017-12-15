"""
This sub-module contains the :py:class:`Kentauros` class, which holds configuration values parsed
from CLI arguments, environment variables and configuration files. The implementation makes sure
that command line arguments, environment variables and configuration files are parsed only once per
program run. Additionally, this subpackage holds logging and error printing functions.
"""


import configparser
import os
import warnings

from collections import OrderedDict

from .init.cli import CLIArgs
from .init.env import get_env_debug, get_env_verby
from .state import KtrState


def __smaller_int__(int1: int, int2: int):
    if int1 < int2:
        return int1
    else:
        return int2


class Kentauros:
    """
    This class stores settings and variables that must be the same during the execution of code from
    the "kentauros" package. This is accomplished by storing the critical data in a class variable,
    which is initialised only once per execution.
    """

    initialised = False
    workdir = os.getcwd()

    cli = None
    debug = None
    verby = None
    conf = None
    packages = None

    def __init__(self):
        warnings.warn("This class is deprecated. Use KtrContext instead.", DeprecationWarning)

        if not Kentauros.initialised:
            Kentauros.cli = CLIArgs()
            Kentauros.debug = get_env_debug() or self.cli.get_debug()
            Kentauros.verby = __smaller_int__(get_env_verby(), self.cli.get_verby())
            Kentauros.packages = OrderedDict()

            config_path = os.path.join(self.workdir, "kentaurosrc")

            if os.path.exists(config_path):
                Kentauros.conf = configparser.ConfigParser(interpolation=None)
                Kentauros.conf.read(config_path)

            Kentauros.initialised = True

    def get_basedir(self) -> str:
        """
        This method tries to parse the kentauros configuration file for a specified base
        directory. If it is not specified, it returns the current directory as a fallback value.

        Returns:
            str:    kentauros base directory
        """

        if self.conf is None:
            return Kentauros.workdir

        try:
            path = self.conf.get("main", "basedir")
        except KeyError:
            return Kentauros.workdir

        if path == "./":
            path = Kentauros.workdir
        elif path[0:2] == "./":
            path = os.path.join(Kentauros.workdir, path[2:])
        elif not os.path.isabs(path):
            path = os.path.join(Kentauros.workdir, path)

        return path

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

    def add_package(self, conf_name: str, package):
        """
        This method adds a package to the list of packages known to the kentauros instance.

        Arguments:
            conf_name:  package configuration name
            package:    Package object

        Returns:
            bool:       successful addition to package list
        """

        if self.debug:
            assert isinstance(conf_name, str)

        if conf_name in self.packages:
            return False

        self.packages[conf_name] = package
        return True

    def get_package(self, conf_name: str):
        """
        This method gets a package from the list of packages known to the kentauros instance.

        Arguments:
            conf_name:  package configuration name

        Returns:
            Package:    package object
        """

        if conf_name not in self.packages:
            return None

        return self.packages[conf_name]

    def get_package_names(self):
        """
        This method gets the list of known package configuration names.

        Returns:
            list:   list of package configurations active in this instance
        """

        return self.packages.keys()

    def state_read(self, conf_name: str) -> dict:
        """
        This method reads the entries for the given package from the database and returns them as
        an ordered dictionary.

        Arguments:
            str conf_name:  package configuration name

        Returns:
            dict:           result of the query
        """

        state = KtrState(os.path.join(self.get_basedir(), "state.json"))
        return state.read(conf_name)

    def state_write(self, conf_name: str, entries: dict):
        """
        This method inserts or updates a package's entry in the state database with the dictionary
        entries given.

        Arguments:
            str package:    package configuration name
            dict entries:   dict containing the key-value pairs to insert or update in the db

        Returns:
            int:            ID of the package in the database
        """

        state = KtrState(os.path.join(self.get_basedir(), "state.json"))
        state.write(conf_name, entries)

    def state_delete(self, conf_name: str):
        """
        This method deletes the entries for the given package from the database and returns its ID.

        Arguments:
            str conf_name:  package configuration name

        Returns:
            int:            ID of the removed entry
        """

        state = KtrState(os.path.join(self.get_basedir(), "state.json"))
        state.remove(conf_name)
