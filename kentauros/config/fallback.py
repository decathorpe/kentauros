"""
kentauros.config.fallback
this KtrConf is used if looking in all other places yields no (usable) results.
it defaults to using "./" as default directory for confdir, datadir, specdir.
"""

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType


def get_fallback_config():
    """
    kentauros.config.fallback.get_fallback_config():
    function that returns fallback values for kentauros configuration
    """
    result = KtrConf()
    result.add_section("main")
    result.set("main", "basedir", "./")
    result.set("main", "confdir", "./")
    result.set("main", "datadir", "./")
    result.set("main", "packdir", "./")
    result.set("main", "specdir", "./")
    result.type = KtrConfType.FALLBACK
    return result

