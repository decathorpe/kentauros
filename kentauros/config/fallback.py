"""
This module contains :py:func:`get_fallback_config` function, which returns a
:py:class:`KtrConf` instance containing the current directory as fallback value.
"""


import os

from kentauros.definitions import KtrConfType
from kentauros.config.common import KtrConf


LOG_PREFIX1 = "ktr/config/fallback: "
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


def get_fallback_config() -> KtrConf:
    """
    This function provides fallback values for kentauros instance settings and puts them into a
    :py:class:`KtrConf` instance for further processing.

    Returns:
        KtrConf: fallback settings
    """

    result = KtrConf(KtrConfType.FALLBACK, basedir=os.path.abspath("./"))

    if result.validate():
        return result
    else:
        print(LOG_PREFIX1 + "Something went horribly wrong here.", flush=True)
        return None
