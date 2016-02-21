"""
kentauros.config.envvar
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os
from kentauros.config.common import KtrConf, KtrConfType


ENV_BASEDIR = os.environ.get("KTR_BASE_DIR")
ENV_CONFDIR = os.environ.get("KTR_CONF_DIR")
ENV_DATADIR = os.environ.get("KTR_DATA_DIR")
ENV_PACKDIR = os.environ.get("KTR_PACK_DIR")
ENV_SPECDIR = os.environ.get("KTR_SPEC_DIR")


def get_env_config():
    """
    kentauros.config.env.get_env_config():
    function that returns a KtrConf object containing ENV_????_DIR settings
    """
    if (ENV_BASEDIR == None) and \
       (ENV_CONFDIR == None) and \
       (ENV_DATADIR == None) and \
       (ENV_PACKDIR == None) and \
       (ENV_SPECDIR == None):
        return None
    else:
        result = KtrConf()
        result['main'] = {}
        result['main']['basedir'] = ENV_BASEDIR
        result['main']['confdif'] = ENV_CONFDIR
        result['main']['datadir'] = ENV_DATADIR
        result['main']['packdir'] = ENV_PACKDIR
        result['main']['specdir'] = ENV_SPECDIR
        result.type = KtrConfType.ENV
        return result

