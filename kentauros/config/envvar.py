"""
This module contains :py:func:`get_env_config` function, which parses
environment variables for settings. Those settings include - at the moment -
the base directory for kentauros data (`KTR_BASEDIR`), the directory for package
configuration files (`KTR_CONFDIR`), the directory for package sources
(`KTR_DATADIR`), the directory for buildable source packages (`KTR_PACKDIR`)
and the package specification directory (`KTR_SPECDIR`).
"""


import os

from kentauros.definitions import KtrConfType
from kentauros.config.common import KtrConf


LOGPREFIX1 = "ktr/config/envvar: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def get_env_config() -> KtrConf:
    """
    This function reads and parses environment variables and puts them into a
    :py:class:`KtrConf` instance for further processing.

    Returns:
        KtrConf: settings parsed from environment variables
    """

    env_basedir = os.environ.get("KTR_BASE_DIR")
    env_confdir = os.environ.get("KTR_CONF_DIR")
    env_datadir = os.environ.get("KTR_DATA_DIR")
    env_packdir = os.environ.get("KTR_PACK_DIR")
    env_specdir = os.environ.get("KTR_SPEC_DIR")

    # if no settings were set by env variables, return None
    if (env_basedir is None) and \
       (env_confdir is None) and \
       (env_datadir is None) and \
       (env_packdir is None) and \
       (env_specdir is None):
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    if env_basedir is not None:
        result = KtrConf(KtrConfType.ENV,
                         basedir=os.path.abspath(env_basedir))

        if env_confdir is not None:
            result.confdir = os.path.abspath(env_confdir)
        if env_datadir is not None:
            result.datadir = os.path.abspath(env_datadir)
        if env_packdir is not None:
            result.packdir = os.path.abspath(env_packdir)
        if env_specdir is not None:
            result.specdir = os.path.abspath(env_specdir)

    # basedir not set: all other dirs must be specified
    else:
        result = KtrConf(KtrConfType.ENV)
        result.confdir = os.path.abspath(env_confdir)
        result.datadir = os.path.abspath(env_datadir)
        result.packdir = os.path.abspath(env_packdir)
        result.specdir = os.path.abspath(env_specdir)

    if result.validate():
        return result
    else:
        print(LOGPREFIX1 +
              "Not all neccessary config values " +
              "have been set by env variables.")
        return None
