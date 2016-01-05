"""
kentauros.config.common
this file contains common functions, definitions, classes and methods for
all configuration methods.
"""

import configparser
from enum import Enum
import os

from kentauros.init import dbg, err
from kentauros.init.env import HOME


def __replace_home__(string):
    if "$HOME" in string:
        newstring = string.replace("$HOME", HOME)
    elif "~" in string:
        newstring = string.replace("~", HOME)
    return newstring


class KtrConfType(Enum):
    """
    kentauros.config.base.KtrConfType
    enum that defines all possible configuration sources.
    """
    CLI = 1
    ENV = 2
    PROJECT = 3
    USER = 4
    SYSTEM = 5
    DEFAULT = 6
    FALLBACK = 7


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
        self.specdir = ""
        self.type = None

    def succby(self, other):
        """
        kentauros.config.common.KtrConf.succby()
        method that replaces config values in this KtrConf (self) with non-None
          config values from another KtrConf (other)
        """
        assert isinstance(other, KtrConf)
        if other.confdir != None:
            dbg("config: confdir overridden by value in" + repr(other))
            self.confdir = other.confdir
        if other.datadir != None:
            dbg("config: datadir overridden by value in" + repr(other))
            self.datadir = other.datadir
        if other.specdir != None:
            dbg("config: specdir overridden by value in" + repr(other))
            self.specdir = other.specdir

    def read(self, filepath, conftype):
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
            raise FileNotFoundError

        configfile = configparser.ConfigParser()
        configfile.read(filepath)

        self.type = conftype

        errors = 0

        try:
            self.confdir = configfile['main']['confdir']
            self.confdir = __replace_home__(self.confdir)
        except KeyError:
            err("Configuration file does not contain main section or confdir value.")
            errors += 1

        try:
            self.datadir = configfile['main']['datadir']
            self.datadir = __replace_home__(self.datadir)
        except KeyError:
            err("Configuration file does not contain main section or datadir value.")
            errors += 1

        try:
            self.specdir = configfile['main']['specdir']
            self.specdir = __replace_home__(self.specdir)
        except KeyError:
            err("Configuration file does not contain main section or specdir value.")
            errors += 1

        if not errors:
            return False
        else:
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

