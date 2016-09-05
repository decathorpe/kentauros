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

    # if no settings were set by env variables, return None
    if env_basedir is None:
        return None

    # if at least basedir has been set, construct KtrConf from CLI switches
    result = None
    if env_basedir is not None:
        result = KtrConf(KtrConfType.ENV, basedir=os.path.abspath(env_basedir))

    if result is None:
        return None

    if result.validate():
        return result
    else:
        print(LOGPREFIX1 + "Something went wrong during configuration parsing.")
        return None
