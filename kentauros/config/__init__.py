"""
kentauros.config module
explicitly determines order in which configurations are read.
later items in the list can override already determined configuration,
or act as fallback if none has been found so far.
"""

from collections import OrderedDict
import configparser
from enum import Enum
import os

from kentauros.init import dbg, err
from kentauros.init.cli import CLI_PREF_CONF
from kentauros.config import cli, default, envvar, fallback, project, system, user
from kentauros.config.common import KtrConfType


__all__ = []


# configurations, in ascending priority
KTR_CONF_DICT = OrderedDict()
KTR_CONF_DICT[KtrConfType.FALLBACK] = fallback.CONF
KTR_CONF_DICT[KtrConfType.DEFAULT] = default.CONF
KTR_CONF_DICT[KtrConfType.SYSTEM] = system.CONF
KTR_CONF_DICT[KtrConfType.USER] = user.CONF
KTR_CONF_DICT[KtrConfType.PROJECT] = project.CONF
KTR_CONF_DICT[KtrConfType.ENV] = envvar.CONF
KTR_CONF_DICT[KtrConfType.CLI] = cli.CONF


# KTR_CONF contains the highest-priority, non-None configuration for every value
KTR_CONF = fallback.CONF
for conftype in KTR_CONF_DICT:
    conf = KTR_CONF_DICT[conftype]
    if conf != None:
        KTR_CONF.succby(conf)


if CLI_PREF_CONF:
    CONFTYPE = None

    # check if requirested config type is in Enum
    try:
        CONFTYPE = KtrConfType[CLI_PREF_CONF]
    except KeyError:
        err("Configuration type not supported.")
        err("Try one of: default, system, user, project, cli, env")

    KTR_CONF_NEW = None
    # check if requirested config type is in Dict
    try:
        KTR_CONF_NEW = KTR_CONF_DICT[CONFTYPE]
    except KeyError:
        err("Unknown error occurred, requested configuration not in list.")

    print(KTR_CONF_NEW)
    if KTR_CONF_NEW:
        # only apply preferred configuration if it is not None
        KTR_CONF = KTR_CONF_NEW
    else:
        err("Preferred configuration file does not exist or is not valid.")

