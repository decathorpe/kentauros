"""
kentauros.config module
explicitly determines order in which configurations are read.
later items in the list can override already determined configuration,
or act as fallback if none has been found so far.
"""


import os


__all__ = []

def init_dirs(basedir):
    """
    kentauros.init.dirs()
    """
    if not os.access(basedir, os.R_OK):
        os.mkdir(basedir)
    if not os.access(os.path.join(basedir + "sources"), os.W_OK):
        os.mkdir(os.path.join(basedir + "sources"))
    if not os.access(os.path.join(basedir + "configs"), os.W_OK):
        os.mkdir(os.path.join(basedir + "configs"))

