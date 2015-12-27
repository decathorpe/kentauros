"""
kentauros.config.system
reads /etc/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import configparser
import os

from kentauros.config.base import KtrConf, KtrConfType


DEFAULT_CONF = KtrConf()


