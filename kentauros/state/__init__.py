"""
This subpackage contains classes and functions for reading and writing state to the projects
database.
"""


import os
from collections import OrderedDict

import dataset

from kentauros.instance import Kentauros


LOGPREFIX = "ktr/state"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


STATE_DB_PROTOCOL = "sqlite:///"
STATE_DB_URL = "state.sqlite"


class KtrStater:
    """
    This is a helper class for writing to and reading from the projects state database (which is, by
    default, a SQLite file).
    """

    def __init__(self):
        self.db_path = os.path.join(Kentauros(LOGPREFIX).conf.get_basedir(), STATE_DB_URL)
        self.db_conn = dataset.connect(STATE_DB_PROTOCOL + self.db_path)
        self.pkg_tbl = self.db_conn["packages"]

    def write(self, conf_name: str, entries: dict) -> int:
        """
        This method inserts or updates a package's entry in the state database with the dictionary
        entries given.

        Arguments:
            str package:    package name
            dict entries:   dictionary containing the key-value pairs to insert or update in the db

        Returns:
            int: row ID of the package in the database
        """

        entries["conf_name"] = conf_name
        return self.pkg_tbl.upsert(entries, ["conf_name"])

    def read(self, conf_name: str) -> OrderedDict:
        """
        This method reads the entries for the given package from the database and returns them as an
        ordered dictionary.

        Arguments:
            str conf_name:  package configuration name

        Returns:
            OrderedDict:    result of the query
        """

        return self.pkg_tbl.find_one(conf_name=conf_name)
