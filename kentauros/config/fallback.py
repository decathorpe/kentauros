"""
kentauros.config.fallback
this KtrConf is used if looking in all other places yields no (usable) results.
it defaults to using "./" as default directory for confdir, datadir, specdir.
"""

from kentauros.config.common import KtrConf, KtrConfType


def get_fallback_config():
    """
    kentauros.config.fallback.get_fallback_config():
    function that returns fallback values for kentauros configuration
    """
    result = KtrConf()
    result['main'] = {}
    result['main']['basedir'] = "./"
    result['main']['confdir'] = "./"
    result['main']['datadir'] = "./"
    result['main']['specdir'] = "./"
    result.type = KtrConfType.FALLBACK
    return result

