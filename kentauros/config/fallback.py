"""
kentauros.config.fallback
this KtrConf is used if looking in all other places yields no (usable) results.
it defaults to using "./" as default directory for confdir, datadir, specdir.
"""

from kentauros.config.common import KtrConf, KtrConfType


CONF = KtrConf()
CONF.confdir = "./"
CONF.datadir = "./"
CONF.specdir = "./"
CONF.type = KtrConfType.FALLBACK

