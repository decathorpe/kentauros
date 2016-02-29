"""
kentauros.config.envvar
reads environment variables to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import os

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType


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
    # if no settings were set by env variables, return None
    if (ENV_BASEDIR == None) and \
       (ENV_CONFDIR == None) and \
       (ENV_DATADIR == None) and \
       (ENV_PACKDIR == None) and \
       (ENV_SPECDIR == None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if ENV_BASEDIR != None:
        result = KtrConf()
        result.add_section("main")
        result.set("main", "basedir", os.path.abspath(ENV_BASEDIR))

        if ENV_CONFDIR == None:
            result.set("main", "confdir", os.path.join(result['main']['basedir'], "configs"))
        else:
            result.set("main", "confdir", ENV_CONFDIR)

        if ENV_DATADIR == None:
            result.set("main", "datadir", os.path.join(result['main']['basedir'], "sources"))
        else:
            result.set("main", "datadir", ENV_DATADIR)

        if ENV_PACKDIR == None:
            result.set("main", "packdir", os.path.join(result['main']['basedir'], "packages"))
        else:
            result.set("main", "packdir", ENV_PACKDIR)

        if ENV_SPECDIR == None:
            result.set("main", "specdir", os.path.join(result['main']['basedir'], "specs"))
        else:
            result.set("main", "specdir", ENV_SPECDIR)

        result.type = KtrConfType.ENV
        return result

    # default case: mix-and-match of set and not set config values
    else:
        result = KtrConf()
        result['main'] = {}
        result.set("main", "basedir", ENV_BASEDIR)
        result.set("main", "confdir", ENV_CONFDIR)
        result.set("main", "datadir", ENV_DATADIR)
        result.set("main", "packdir", ENV_PACKDIR)
        result.set("main", "specdir", ENV_SPECDIR)
        result.type = KtrConfType.ENV
        return result

