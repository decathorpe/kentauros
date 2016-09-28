"""
This submodule contains the :py:class:`Kentauros` class, which holds configuration values parsed
from CLI arguments, environment variables and configuration files. The implementation makes sure
that command line arguments, environment variables and configuration files are parsed only once per
program run. Additionally, this subpackage holds logging and error printing functions.
"""


import os
import warnings

from tinydb import TinyDB, Query

from kentauros.config import ktr_get_conf
from kentauros.init.cli import CLIArgs
from kentauros.init.env import get_env_debug, get_env_verby


LOGPREFIX = "ktr/instance"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


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

    cli = None
    debug = None
    verby = None
    conf = None
    packages = None

    def __init__(self):
        if not Kentauros.initialised:
            Kentauros.cli = CLIArgs()
            Kentauros.debug = get_env_debug() or self.cli.get_debug()
            Kentauros.verby = __smaller_int__(get_env_verby(), self.cli.get_verby())
            Kentauros.conf = ktr_get_conf()
            Kentauros.packages = dict()

            Kentauros.initialised = True

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
            from kentauros.package import Package
            assert isinstance(conf_name, str)
            assert isinstance(package, Package)

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

    def state_write(self, conf_name: str, entries: dict) -> int:
        """
        This method inserts or updates a package's entry in the state database with the dictionary
        entries given.

        Arguments:
            str package:    package configuration name
            dict entries:   dict containing the key-value pairs to insert or update in the db

        Returns:
            int:            ID of the package in the database
        """

        with TinyDB(os.path.join(self.conf.get_basedir(), "state.json")) as db:
            package = Query()
            if not db.search(package.name == conf_name):
                entries["name"] = conf_name
                return db.insert(entries)
            else:
                return db.update(entries, package.name == conf_name)[0]

    def state_read(self, conf_name: str) -> dict:
        """
        This method reads the entries for the given package from the database and returns them as
        an ordered dictionary.

        Arguments:
            str conf_name:  package configuration name

        Returns:
            dict:           result of the query
        """

        assert isinstance(conf_name, str)

        with TinyDB(os.path.join(self.conf.get_basedir(), "state.json")) as db:
            package = Query()
            results = db.search(package.name == conf_name)

        if len(results) > 1:
            warnings.warn("Got more than one result from the state db. Something went wrong here.",
                          Warning)
            return results[0]
        elif len(results) == 0:
            warnings.warn("Got no result from the state db. Package state not yet stored.", Warning)
            return None
        else:
            return results[0]
