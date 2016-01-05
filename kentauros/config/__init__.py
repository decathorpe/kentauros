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
from kentauros.config.common import KtrConf, KtrConfType


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


def get_pref_conf(pref_conf):
    """
    kentauros.config.get_pref_conf()
    get and return preferred-by-CLI configuration
    """

    # check if requirested config type is in Enum
    try:
        conf_type = KtrConfType[pref_conf]
    except KeyError:
        err("Configuration type not supported.")
        err("Try one of: default, system, user, project, cli, env")

    # getr requested config from Dict
    ktr_conf_new = KTR_CONF_DICT[conf_type]

    # apply it if it is not None
    if ktr_conf_new:
        return ktr_conf_new


def get_conf():
    """
    kentauros.config.get_conf()
    get and return highest-priority configuration for every config value
    """

    if CLI_PREF_CONF:
        return get_pref_conf(CLI_PREF_CONF)

    # KTR_CONF should contain the highest-priority,
    # non-None configuration for every value
    ktr_conf = fallback.CONF
    for conftype in KTR_CONF_DICT:
        # skip FALLBACK config
        if conftype != KtrConfType.FALLBACK:
            conf = KTR_CONF_DICT[conftype]
            if conf != None:
                ktr_conf.succby(conf)

    return ktr_conf


KTR_CONF = get_conf()

