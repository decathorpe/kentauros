"""
kentauros.config.fallback
reads ./kentaurosrc to eventually determine location of
- configuration files
- source directories / tarballs
as fallback method, if everything else fails, or is set by CLI option.
"""

from kentauros.config import KtrConf


FALLBACK_CONF = KtrConf()
FALLBACK_CONF.basedir = "./"
FALLBACK_CONF.confdir = "./"
FALLBACK_CONF.datadir = "./"

