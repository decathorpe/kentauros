"""
kentauros.config module
explicitly determines order in which configurations are read.
later items in the list can override already determined configuration,
or act as fallback if none has been found so far.
"""


__all__ = ["defaults", "environ", "fallback", "rcfile", "xdgconfig"]


class KtrConf:
    def __init__(self):
        self.basedir = ""
        self.confdir = ""
        self.datadir = ""

