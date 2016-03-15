"""
kentauros.config.envvar file
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os

from kentauros.definitions import KtrConfType
from kentauros.config.common import KtrConf


ENV_BASEDIR = os.environ.get("KTR_BASE_DIR")
ENV_CONFDIR = os.environ.get("KTR_CONF_DIR")
ENV_DATADIR = os.environ.get("KTR_DATA_DIR")
ENV_PACKDIR = os.environ.get("KTR_PACK_DIR")
ENV_SPECDIR = os.environ.get("KTR_SPEC_DIR")


LOGPREFIX1 = "ktr/config/envvar: "


def get_env_config():
    """
    kentauros.config.envvar.get_env_config():
    function that returns a KtrConf object containing ENV settings
    """
    # if no settings were set by env variables, return None
    if (ENV_BASEDIR is None) and \
       (ENV_CONFDIR is None) and \
       (ENV_DATADIR is None) and \
       (ENV_PACKDIR is None) and \
       (ENV_SPECDIR is None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if ENV_BASEDIR != None:
        result = KtrConf(KtrConfType.ENV,
                         basedir=os.path.abspath(ENV_BASEDIR))

        if ENV_CONFDIR is not None:
            result.confdir = ENV_CONFDIR
        if ENV_DATADIR is not None:
            result.datadir = ENV_DATADIR
        if ENV_PACKDIR is not None:
            result.packdir = ENV_PACKDIR
        if ENV_SPECDIR is not None:
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
        print(LOGPREFIX1 + \
            "Not all neccessary config values have been set by env variables.")
        return None

