"""
kentauros.config.envvar
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os
from kentauros.config.common import KtrConf, KtrConfType


CONF = KtrConf()
CONF.confdir = os.environ.get("KTR_CONF_DIR")
CONF.datadir = os.environ.get("KTR_DATA_DIR")
CONF.type = KtrConfType.CLI_CONF

if (CONF.confdir is None) or (CONF.datadir is None):
    CONF = None

