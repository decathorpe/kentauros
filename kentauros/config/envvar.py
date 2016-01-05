"""
kentauros.config.envvar
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os
from kentauros.config.common import KtrConf, KtrConfType


CONF = KtrConf()

ENV_CONFDIR = os.environ.get("KTR_CONF_DIR")
ENV_DATADIR = os.environ.get("KTR_DATA_DIR")
ENV_SPECDIR = os.environ.get("KTR_SPEC_DIR")


if (ENV_CONFDIR == None) and (ENV_DATADIR == None) and (ENV_SPECDIR == None):
    CONF = None
else:
    CONF.confdir = ENV_CONFDIR
    CONF.datadir = ENV_DATADIR
    CONF.specdir = ENV_SPECDIR
    CONF.type = KtrConfType.ENV

