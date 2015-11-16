"""
kentauros.config.environ
reads environment variables to eventually determine location of
- configuration files
- source directories / tarballs
"""

import os
from kentauros.config import KtrConf


ENVIRON_CONF = KtrConf()
ENVIRON_CONF.basedir = os.environ.get("HOME")
ENVIRON_CONF.confdir = os.environ.get("KTR_CONF_DIR")
ENVIRON_CONF.datadir = os.environ.get("KTR_DATA_DIR")

if (ENVIRON_CONF.confdir is None) and (ENVIRON_CONF.datadir is None):
    ENVIRON_CONF = None

