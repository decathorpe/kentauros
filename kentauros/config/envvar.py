"""
kentauros.config.envvar
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType
from kentauros.init import log


ENV_BASEDIR = os.environ.get("KTR_BASE_DIR")
ENV_CONFDIR = os.environ.get("KTR_CONF_DIR")
ENV_DATADIR = os.environ.get("KTR_DATA_DIR")
ENV_PACKDIR = os.environ.get("KTR_PACK_DIR")
ENV_SPECDIR = os.environ.get("KTR_SPEC_DIR")


LOGPREFIX1 = "ktr/config/envvar: "


def get_env_config():
    """
    kentauros.config.env.get_env_config():
    function that returns a KtrConf object containing ENV_????_DIR settings
    """
    # if no settings were set by env variables, return None
    if (ENV_BASEDIR == None) and \
       (ENV_CONFDIR == None) and \
       (ENV_DATADIR == None) and \
       (ENV_PACKDIR == None) and \
       (ENV_SPECDIR == None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if ENV_BASEDIR != None:
        result = KtrConf(KtrConfType.ENV,
                         basedir=os.path.abspath(ENV_BASEDIR))

        if ENV_CONFDIR != None:
            result.confdir = ENV_CONFDIR
        if ENV_DATADIR != None:
            result.datadir = ENV_DATADIR
        if ENV_PACKDIR != None:
            result.packdir = ENV_PACKDIR
        if ENV_SPECDIR != None:
            result.specdir = ENV_SPECDIR

    # basedir not set: all other dirs must be specified
    else:
        result = KtrConf(KtrConfType.ENV)
        result.confdir = ENV_CONFDIR
        result.datadir = ENV_DATADIR
        result.packdir = ENV_PACKDIR
        result.specdir = ENV_SPECDIR

    if result.validate():
        return result
    else:
        log(LOGPREFIX1 + "Not all neccessary config values have been set by env variables.")
        return None

