"""
This subpackage contains classes and functions for reading and writing state to
the project's SQLite database.
"""

import dataset
import os

from collections import OrderedDict

from kentauros.instance import Kentauros


STATE_DB_FILE_NAME = "state.sqlite"


class KtrStater:
    path = os.path.join(Kentauros().conf.basedir, STATE_DB_FILE_NAME)

    def __init__(self):
        self.db = dataset.connect("sqlite:///" + KtrStater.path)
        self.tb = self.db["packages"]

    def write(self, package: str, entries: dict) -> int:
        entries["package"] = package
        return self.tb.upsert(entries, ["package"])

    def read(self, package: str) -> OrderedDict:
        return self.tb.find_one(package=package)
