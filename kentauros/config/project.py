"""
kentauros.config.project
reads project-specific ./kentaurosrc to eventually determine location of
- configuration files (confdir)
- source directories / tarballs (datadir)
"""

import configparser
import os

from kentauros.base import dbg, err
from kentauros.config.base import KtrConf, KtrConfType


FILE_PATH = "./kentaurosrc"
ERR_MSG = "This directory does not contain a kentaurosrc file, or it is not readable."


def read_conf(force=False):
    """
    kentauros.config.project.read_conf()
    function that reads local (project-specific) configuration file and parses
        the options.
    - if file is not present:
        - if force=True is specified: OSError is raised.
        - else: a debug message might be displayed. returns None.
    - if file is present but does not contain neccessary keys:
        returns None.
    returns a KtrConf object.
    """
    file_access = os.access(FILE_PATH, os.R_OK)

    if not file_access:
        if not force:
            dbg(ERR_MSG)
            return None
        else:
            raise OSError(ERR_MSG)

    configfile = configparser.ConfigParser()
    configfile.read(FILE_PATH)

    conf = KtrConf()
    conf.type = KtrConfType.PROJECT_CONF

    try:
        conf.confdir = configfile['main']['confdir']
    except KeyError:
        err("Configuration file does not contain main section or confdir value.")
        return None

    try:
        conf.datadir = configfile['main']['datadir']
    except KeyError:
        err("Configuration file does not contain main section or datadir value.")
        return None

    return conf

