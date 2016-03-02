"""
kentauros.config.fallback
this KtrConf is used if looking in all other places yields no (usable) results.
it defaults to using "./" as default directory for confdir, datadir, specdir.
"""

import os

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType
from kentauros.init import log


LOGPREFIX1 = "ktr/config/fallback: "


def get_fallback_config():
    """
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
        log(LOGPREFIX1 + "Something went horribly wrong here.")
        return None

