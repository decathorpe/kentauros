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


KTR_CONF_LIST = [default.CONF,
                 system.CONF,
                 user.CONF,
                 project.CONF,
                 envvar.CONF,
                 cli.CONF]

