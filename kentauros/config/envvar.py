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
CONF.specdir = os.environ.get("KTR_SPEC_DIR")

CONF.type = KtrConfType.ENV

