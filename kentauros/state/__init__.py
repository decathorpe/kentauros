"""
This subpackage contains classes and functions for reading and writing state to
the project's SQLite database.
"""

import os
from collections import OrderedDict

import dataset

from kentauros.instance import Kentauros


STATE_DB_FILE_NAME = "state.sqlite"


class KtrStater:
    """
    This is a helper class for writing to and reading from the project's
    state database (which is a SQLite file).
    """

    def __init__(self):
        self.path = os.path.join(Kentauros().conf.basedir, STATE_DB_FILE_NAME)
        self.db_conn = dataset.connect("sqlite:///" + self.path)
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
