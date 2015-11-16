"""
kentauros.config.rcfile
reads $HOME/.kentaurosrc to eventually determine location of
- configuration files
- source directories / tarballs
"""

import configparser
import os
from kentauros.config import KtrConf


RC_CONF = KtrConf()

with os.environ.get("HOME") as HOME_PATH:
    with os.path.join(HOME_PATH, ".kentaurosrc") as RC_FILE_PATH:
        with configparser.ConfigParser() as RC_CONFIG:
            RC_CONFIG.read(RC_FILE_PATH)

            if "paths" in RC_CONFIG:
                if "home" in RC_CONFIG["paths"]:
                    RC_CONF.basedir = RC_CONFIG["paths"]["home"]
                else:
                    RC_CONF = None

                if "configs" in RC_CONFIG["paths"]:
                    RC_CONF.confdir = RC_CONFIG["paths"]["configs"]
                else:
                    RC_CONF = None

                if "sources" in RC_CONFIG["paths"]:
                    RC_CONF.datadir = RC_CONFIG["paths"]["sources"]
                else:
                    RC_CONF = None

            else:
                RC_CONF = None

