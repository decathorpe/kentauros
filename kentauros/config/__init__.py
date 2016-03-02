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

from kentauros.definitions import KTR_SYSTEM_DATADIR

from kentauros.config import cli, envvar, fallback
from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType

from kentauros.init import dbg, err, log
from kentauros.init.cli import CLI_ARGS
from kentauros.init.env import HOME


__all__ = []


DEFAULT_FILE_PATH = os.path.join(KTR_SYSTEM_DATADIR, "default.conf")
PROJECT_FILE_PATH = os.path.abspath("./kentaurosrc")
SYSTEM_FILE_PATH = "/etc/kentaurosrc"
USER_FILE_PATH = os.path.join(HOME, ".config/kentaurosrc")

DEFAULT_ERR_MSG = DEFAULT_FILE_PATH + " does not exist or it is not readable."
PROJECT_ERR_MSG = "This directory does not contain a kentaurosrc file, or it is not readable."
SYSTEM_ERR_MSG = SYSTEM_FILE_PATH + " does not exist or is not readable."
USER_ERR_MSG = USER_FILE_PATH + " does not exist or is not readable."


LOGPREFIX1 = "ktr/config: "
LOGPREFIX2 = "            - "


# configurations, in ascending priority
KTR_CONF_DICT = OrderedDict()

KTR_CONF_DICT[KtrConfType.FALLBACK] = fallback.get_fallback_config()
KTR_CONF_DICT[KtrConfType.DEFAULT] = KtrConf(KtrConfType.DEFAULT).from_file(DEFAULT_FILE_PATH,
                                                                            DEFAULT_ERR_MSG)
KTR_CONF_DICT[KtrConfType.SYSTEM] = KtrConf(KtrConfType.SYSTEM).from_file(SYSTEM_FILE_PATH,
                                                                          SYSTEM_ERR_MSG)
KTR_CONF_DICT[KtrConfType.USER] = KtrConf(KtrConfType.USER).from_file(USER_FILE_PATH,
                                                                      USER_ERR_MSG)
KTR_CONF_DICT[KtrConfType.PROJECT] = KtrConf(KtrConfType.PROJECT).from_file(PROJECT_FILE_PATH,
                                                                            PROJECT_ERR_MSG)
KTR_CONF_DICT[KtrConfType.ENV] = envvar.get_env_config()
KTR_CONF_DICT[KtrConfType.CLI] = cli.get_cli_config()


def get_pref_conf(pref_conf):
    """
    kentauros.config.get_pref_conf()
    get and return preferred-by-CLI configuration
    """

    # check if requirested config type is in Enum
    try:
        conf_type = KtrConfType[pref_conf]
    except KeyError:
        err(LOGPREFIX1 + "Configuration type not supported.")
        err(LOGPREFIX1 + "Supported: default, system, user, project, cli, env")

    # get requested config from Dict
    ktr_conf = KTR_CONF_DICT[conf_type]

    # apply it if it is not None
    if ktr_conf != None:
        return ktr_conf
    else:
        return None


def ktr_get_conf():
    """
    kentauros.config.get_conf()
    get and return highest-priority configuration for every config value
    """

    if CLI_ARGS['priconf']:
        ktr_conf = get_pref_conf(CLI_ARGS['priconf'])

    if ktr_conf != None:
        return ktr_conf

    # KTR_CONF should contain the highest-priority,
    # non-None configuration for every value
    ktr_conf = KTR_CONF_DICT[KtrConfType.FALLBACK]

    for conftype in KTR_CONF_DICT:
        # skip FALLBACK config
        if conftype == KtrConfType.FALLBACK:
            continue

        conf = KTR_CONF_DICT[conftype]
        if conf != None:
            ktr_conf.succby(conf)

    return ktr_conf


KTR_CONF = ktr_get_conf()

log("ktr: BASEDIR: " + KTR_CONF.basedir, 0)
log("ktr: CONFDIR: " + KTR_CONF.confdir, 0)
log("ktr: DATADIR: " + KTR_CONF.datadir, 0)
log("ktr: PACKDIR: " + KTR_CONF.packdir, 0)
log("ktr: SPECDIR: " + KTR_CONF.specdir, 0)

