"""
kentauros.source module
contains Source class and methods
Source class contains information about package upstream source and methods to
manipulate them.
"""

import enum

class SourceType(enum.Enum):
    none = 1

class Source():
    def __init__(self):
        self.dest = ""
        self.orig = ""
        self.type = None

