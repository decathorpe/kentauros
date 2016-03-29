"""
# TODO: napoleon module docstring
kentauros.config.fallback
this KtrConf is used if looking in all other places yields no (usable) results.
it defaults to using "./" as default directory for confdir, datadir, specdir.
"""


import os

from kentauros.definitions import KtrConfType
from kentauros.config.common import KtrConf


LOGPREFIX1 = "ktr/config/fallback: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def get_fallback_config():
    """
    # TODO: napoleon function docstring
    kentauros.config.fallback.get_fallback_config():
    function that returns fallback values for kentauros configuration
    """
    result = KtrConf(KtrConfType.FALLBACK,
                     basedir=os.path.abspath("./"))

    result.confdir = os.path.join(result.basedir, "./")
    result.datadir = os.path.join(result.basedir, "./")
    result.packdir = os.path.join(result.basedir, "./")
    result.specdir = os.path.join(result.basedir, "./")

    if result.validate():
        return result
    else:
        print(LOGPREFIX1 + "Something went horribly wrong here.")
        return None

