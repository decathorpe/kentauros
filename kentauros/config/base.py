"""
kentauros.config.base
defines base data structures that hold kentauros configuration:
- Enum "ConfType" containing all types of possible configuration sources
- KtrConf class containing:
  - configuration files (confdir)
  - source directories / tarballs (datadir)
  - may be extended
"""

from enum import Enum
# import os


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

