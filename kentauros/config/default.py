"""
kentauros.config.default
reads /usr/share/kentauros/default.conf to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import configparser
import os

from kentauros.config.base import KtrConf, KtrConfType


