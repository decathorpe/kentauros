"""
This sub-package contains the the :py:class:`Package` class, which encapsulates information about a
package (as the name suggests), as defined by the package's `.conf` configuration file.
"""

import configparser as cp
import os


class Package:
    """
    Arguments:
        str conf_path:  path to the package configuration file (relative or absolute)

    Attributes:
        str conf_path:      path to the package configuration file (relative or absolute)
        str conf_name:      name of the package configuration (path basename stripped of ".conf")
        ConfigParser conf:  ConfigParser object holding the package configuration information
    """

    def __init__(self, conf_path: str):
        assert isinstance(conf_path, str)
        assert os.path.exists(conf_path)
        assert os.access(conf_path, os.R_OK)

        self.conf_path = conf_path

        self.conf = cp.ConfigParser()
        read_path = self.conf.read(conf_path)

        assert read_path == conf_path

        self.conf_name = os.path.basename(conf_path).replace(".conf", "")
