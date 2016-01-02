"""
kentauros.config module
explicitly determines order in which configurations are read.
later items in the list can override already determined configuration,
or act as fallback if none has been found so far.
"""

import configparser
from enum import Enum
import os

from kentauros.base import dbg, err
from kentauros.config import cli, default, envvar, project, system, user


__all__ = []

# configurations, in ascending priority
KTR_CONF_LIST = [default.CONF,
                 system.CONF,
                 user.CONF,
                 project.CONF,
                 envvar.CONF,
                 cli.CONF]

# KTR_CONF contains the highest-priority, non-None configuration
KTR_CONF = None
for conf in KTR_CONF_LIST:
    if conf != None:
        KTR_CONF = conf

