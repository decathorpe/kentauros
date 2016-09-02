"""
This subpackage contains classes and functions for reading and writing state to
the project's SQLite database.
"""

import os
from collections import OrderedDict

import dataset

from kentauros.instance import Kentauros
from kentauros.package import Package


STATE_DB_FILE_NAME = "state.sqlite"


class KtrStater:
    """
    This is a helper class for writing to and reading from the project's
    state database (which is a SQLite file).
    """

    def __init__(self):
        self.db_path = os.path.join(Kentauros().conf.basedir,
                                    STATE_DB_FILE_NAME)
        self.db_conn = dataset.connect("sqlite:///" + self.db_path)
        self.pkg_tbl = self.db_conn["packages"]

    def write(self, package: str, entries: dict) -> int:
        """
        This method inserts or updates a package's entry in the state
        database with the dictionary entries given.

        Arguments:
            str package:    package name
            dict entries:   dictionary containing the key-value pairs to insert
                            or update in the database

        Returns:
            int: row ID of the package in the database
        """

        entries["package"] = package
        return self.pkg_tbl.upsert(entries, ["package"])

    def read(self, package: str) -> OrderedDict:
        """
        This method reads the entries for the given package from the database
        and returns them as an ordered dictionary.

        Arguments:
            str package:    package name

        Returns:
            OrderedDict:    result of the query
        """

        return self.pkg_tbl.find_one(package=package)


class PackageState(dict):
    """
    This :py:class:`dict` subclass contains information about a specific
    package's state, as determined from a :py:class:`Package` object or from
    values read back from the project's state database. It also overrides the
    equality operator for easy comparison of package state objects.
    """

    def __init__(self):
        super().__init__()

        self["name"] = str()
        self["version"] = str()
        self["release"] = str()

    def __eq__(self, other) -> bool:
        for key in self:
            if key not in other:
                return False
            if self[key] != other[key]:
                return False

        for key in other:
            if key not in self:
                return False
            if self[key] != other[key]:
                return False

        return True


# TODO: public function for getting current release (from spec file)

def pkg_state_from_package(pkg: Package) -> PackageState:
    """
    This function produces a :py:class:`PackageState` object from a given
    :py:class:`Package` object.

    Arguments:
        Package pkg:    package to get the state from

    Returns:
        PackageState:   state of the package at the time of the function call
    """

    status = PackageState()
    status["name"] = pkg.name
    status["version"] = pkg.conf.get("version")
    status["release"] = None
    return status


def pkg_state_from_state(name: str) -> PackageState:
    """
    This function produces a :py:class:`PackageState` object from a status that
    has been previously stored in the project's state database.

    Arguments:
        str name:       name of the package to get the saved state for

    Returns:
        PackageState:   state of the package when state was last written to DB
    """

    status = PackageState()

    result = KtrStater().read(name)

    if result is None:
        return None

    status["name"] = name
    status["version"] = result["version"]
    status["release"] = result["release"]

    return status
