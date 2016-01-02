"""
kentauros.config.common
this file contains common functions, definitions, classes and methods for
all configuration methods.
"""

import configparser
from enum import Enum
import os

from kentauros.base import err
from kentauros.init import HOME


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
        self.sysbasedir = ""
        self.sysconfdir = ""
        self.sysdatadir = ""
        self.usrbasedir = ""
        self.usrconfdir = ""
        self.usrdatadir = ""
        self.type = KtrConfType()

    def read(self, filepath, conftype, force=False):
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
            if force:
                raise OSError
            else:
                return None

        configfile = configparser.ConfigParser()
        configfile.read(filepath)

        self.type = conftype

        errors = 0

        try:
            self.sysbasedir = configfile['system']['basedir']
            self.sysbasedir = __replace_home__(self.sysbasedir)
        except KeyError:
            err("Configuration file does not contain system section or confdir value.")
            errors += 1

        try:
            self.sysconfdir = configfile['system']['confdir']
            self.sysconfdir = __replace_home__(self.sysconfdir)
        except KeyError:
            err("Configuration file does not contain system section or confdir value.")
            errors += 1

        try:
            self.sysdatadir = configfile['system']['datadir']
            self.sysdatadir = __replace_home__(self.sysdatadir)
        except KeyError:
            err("Configuration file does not contain system section or datadir value.")
            errors += 1

        try:
            self.usrbasedir = configfile['user']['basedir']
            self.usrbasedir = __replace_home__(self.usrbasedir)
        except KeyError:
            err("Configuration file does not contain user section or confdir value.")
            errors += 1

        try:
            self.usrconfdir = configfile['user']['confdir']
            self.usrconfdir = __replace_home__(self.usrconfdir)
        except KeyError:
            err("Configuration file does not contain user section or confdir value.")
            errors += 1

        try:
            self.usrdatadir = configfile['user']['datadir']
            self.usrdatadir = __replace_home__(self.usrdatadir)
        except KeyError:
            err("Configuration file does not contain user section or datadir value.")
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

