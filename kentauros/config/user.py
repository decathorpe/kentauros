"""
kentauros.config.user
reads $HOME/.config/kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

from kentauros.config.common import KtrConf, KtrConfType

FILE_PATH = "~/.config/kentaurosrc"
ERR_MSG = "$HOME/.config/kentaurosrc does not exist or is not readable."

CONF = KtrConf()
CONF.read(filepath=FILE_PATH,
          conftype=KtrConfType.USER_CONF,
          err_msg=ERR_MSG)

