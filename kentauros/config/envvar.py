"""
kentauros.config.envvar
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os
from kentauros.config.common import KtrConf, KtrConfType


CONF = KtrConf()

CONF.sysbasedir = os.environ.get("KTR_BASE_DIR")
CONF.sysconfdir = os.environ.get("KTR_CONF_DIR")
CONF.sysdatadir = os.environ.get("KTR_DATA_DIR")

CONF.usrbasedir = os.environ.get("KTR_BASE_DIR")
CONF.usrconfdir = os.environ.get("KTR_CONF_DIR")
CONF.usrdatadir = os.environ.get("KTR_DATA_DIR")

CONF.type = KtrConfType.CLI_CONF

if (CONF.sysbasedir is None) or (CONF.sysconfdir is None) or (CONF.sysdatadir is None):
    CONF = None

if (CONF.usrbasedir is None) or (CONF.usrconfdir is None) or (CONF.usrdatadir is None):
    CONF = None

