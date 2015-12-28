"""
kentauros.config.common
this file contains common functions, definitions, classes and methods for
all configuration methods.
"""

import configparser
from enum import Enum
import os

from kentauros.base import dbg, err


class KtrConfType(Enum):
    """
    kentauros.config.base.KtrConfType
    enum that defines all possible configuration sources.
    """
    CLI_CONF = 1
    ENVVAR_CONF = 2
    PROJECT_CONF = 3
    USER_CONF = 4
    SYSTEM_CONF = 5
    DEFAULT_CONF = 6
    FALLBACK_CONF = 7


class KtrConf:
    """
    kentauros.config.base.KtrConf
    class that contains information about kentauros configuration options.
    this includes:
    - location of package configuration files (confdir)
    - location of package source directories / tarballs (datadir)
    - may be extended
    """
    def __init__(self):
        self.confdir = ""
        self.datadir = ""
        self.type = KtrConfType()

    def read(self, filepath, conftype, err_msg, force=False):
        """
        kentauros.config.KtrConf.read()
        method that reads configuration file and parses the options.
        - if file is not present:
            - if force=True is specified: OSError is raised.
            - else: a debug message might be displayed. returns False.
        - if file is present but does not contain neccessary keys:
            returns False.
        returns True if everything worked.
        """
        file_access = os.access(filepath, os.R_OK)

        if not file_access:
            if not force:
                dbg(err_msg)
                return None
            else:
                raise OSError(err_msg)

        configfile = configparser.ConfigParser()
        configfile.read(filepath)

        self.type = conftype

        try:
            self.confdir = configfile['main']['confdir']
        except KeyError:
            err("Configuration file does not contain main section or confdir value.")
            return False

        try:
            self.datadir = configfile['main']['datadir']
        except KeyError:
            err("Configuration file does not contain main section or datadir value.")
            return False

        return True

    def verify(self):
        """
        kentauros.config.base.KtrConf.verify()
        method for verifying valid configuration content.
        """
        print(self)
        # pass
        # check for directory r/w access

    def write(self, dest):
        """
        kentauros.config.base.KtrConf.write()
        method for writing a changed configuration out to a config file.
        """
        assert isinstance(dest, KtrConfType)
        print(self)
        # write config file to dest if type matches and dest is writable

