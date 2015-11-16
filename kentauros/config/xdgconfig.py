"""
kentauros.config.xdgconfig
reads $HOME/.config/kentauros to eventually determine location of
- configuration files
- source directories / tarballs
"""

import os
from kentauros.config import KtrConf


XDG_CONF = KtrConf()

with os.environ.get("HOME") as HOME_PATH:
    XDG_CONF.basedir = HOME_PATH
    XDG_CONF.confdir = os.path.join(HOME_PATH, ".config/kentauros/")
    XDG_CONF.datadir = os.path.join(HOME_PATH, ".local/kentauros/")

