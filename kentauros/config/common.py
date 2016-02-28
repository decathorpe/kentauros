"""
kentauros.config.common
this file contains common functions, definitions, classes and methods for
all configuration methods.
"""

import configparser

from kentauros.definitions import KtrConfType
from kentauros.init import dbg, log
from kentauros.init.env import HOME


LOGPREFIX1 = "ktr/config/common: "
LOGPREFIX2 = "                   - "


def __replace_home__(string):
    if "$HOME" in string:
        newstring = string.replace("$HOME", HOME)
    elif "~" in string:
        newstring = string.replace("~", HOME)
    return newstring


class KtrConf(configparser.ConfigParser): # pylint: disable=too-many-ancestors
    """
    kentauros.config.base.KtrConf
    class that contains information about kentauros configuration options.
    this includes:
    - location of package configuration files (confdir)
    - location of package source directories / tarballs (datadir)
    - may be extended
    """
    def __init__(self):
        super().__init__()
        self.type = None

    def succby(self, other):
        """
        kentauros.config.common.KtrConf.succby()
        method that replaces config values in this KtrConf (self) with non-None
          config values from another KtrConf (other)
        """
        assert isinstance(other, KtrConf)

        for section in other:
            for key in other[section]:
                self[section][key] = other[section][key]
                dbg(LOGPREFIX1 + section + "/" + key + ":" + \
                    " overridden by " + other.type.name + " config")

    def verify(self):
        """
        kentauros.config.base.KtrConf.verify()
        method for verifying valid configuration content.
        """
        print(self)
        # pass
        # check for directory r/w access


def get_config_from_file(filepath, errmsg, conftype):
    """
    kentauros.config.common.get_config_from_file():
    function that reads and returns configuration from filepath
    - prints error message if file does not exist
    - sets type to conftype
    """
    assert isinstance(filepath, str)
    assert isinstance(errmsg, str)
    assert isinstance(conftype, KtrConfType)

    config = KtrConf()
    result = config.read(filepath)

    if result == []:
        log(LOGPREFIX1 + errmsg, 0)
        return None

    else:
        config.type = conftype

        for section in config:
            for key in config[section]:
                config[section][key] = __replace_home__(config[section][key])

        return config

