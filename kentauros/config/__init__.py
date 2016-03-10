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

from kentauros.config.cli import get_cli_config
from kentauros.config.envvar import get_env_config
from kentauros.config.fallback import get_fallback_config

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType

from kentauros.init import dbg, err, log
from kentauros.init.cli import CLI_ARGS
from kentauros.init.env import HOME


__all__ = []


DEF_FILE_PATH = os.path.join(KTR_SYSTEM_DATADIR, "default.conf")
PRJ_FILE_PATH = os.path.abspath("./kentaurosrc")
SYS_FILE_PATH = "/etc/kentaurosrc"
USR_FILE_PATH = os.path.join(HOME, ".config/kentaurosrc")

DEF_ERR_MSG = DEF_FILE_PATH + " does not exist or it is not readable."
PRJ_ERR_MSG = "This directory does not contain a readable kentaurosrc file."
SYS_ERR_MSG = SYS_FILE_PATH + " does not exist or is not readable."
USR_ERR_MSG = USR_FILE_PATH + " does not exist or is not readable."


LOGPREFIX1 = "ktr/config: "
LOGPREFIX2 = "            - "


# configurations, in ascending priority
KTR_CONFS = OrderedDict()

DEFAULT_CONFIG = KtrConf(KtrConfType.DEFAULT).from_file(DEF_FILE_PATH,
                                                        DEF_ERR_MSG)
SYSTEM_CONFIG = KtrConf(KtrConfType.SYSTEM).from_file(SYS_FILE_PATH,
                                                      SYS_ERR_MSG)
USER_CONFIG = KtrConf(KtrConfType.USER).from_file(USR_FILE_PATH,
                                                  USR_ERR_MSG)
PROJECT_CONFIG = KtrConf(KtrConfType.PROJECT).from_file(PRJ_FILE_PATH,
                                                        PRJ_ERR_MSG)

KTR_CONFS[KtrConfType.FALLBACK] = get_fallback_config()
KTR_CONFS[KtrConfType.DEFAULT] = DEFAULT_CONFIG
KTR_CONFS[KtrConfType.SYSTEM] = SYSTEM_CONFIG
KTR_CONFS[KtrConfType.USER] = USER_CONFIG
KTR_CONFS[KtrConfType.PROJECT] = PROJECT_CONFIG
KTR_CONFS[KtrConfType.ENV] = get_env_config()
KTR_CONFS[KtrConfType.CLI] = get_cli_config()


def get_pref_conf(pref_conf):
    """
    kentauros.config.get_pref_conf()
    get and return preferred-by-CLI configuration
    """

    # check if requirested config type is in Enum
    # pylint: disable=unsubscriptable-object
    try:
        conf_type = KtrConfType[pref_conf]
    except KeyError:
        err(LOGPREFIX1 + "Configuration type not supported.")
        err(LOGPREFIX1 + "Supported: default, system, user, project, cli, env")

    # get requested config from Dict
    ktr_conf = KTR_CONFS[conf_type]

    # apply it if it is not None
    if ktr_conf is not None:
        return ktr_conf
    else:
        return None


def ktr_get_conf():
    """
    kentauros.config.get_conf()
    get and return highest-priority configuration for every config value
    """

    ktr_conf = None

    if CLI_ARGS.priconf:
        ktr_conf = get_pref_conf(CLI_ARGS.priconf)

    if ktr_conf is not None:
        return ktr_conf

    # KTR_CONF should contain the highest-priority,
    # non-None configuration for every value
    ktr_conf = KTR_CONFS[KtrConfType.FALLBACK]

    for conftype in KTR_CONFS:
        # skip FALLBACK config
        if conftype == KtrConfType.FALLBACK:
            continue

        conf = KTR_CONFS[conftype]
        if conf is not None:
            ktr_conf.succby(conf)

    return ktr_conf


KTR_CONF = ktr_get_conf()

log("ktr: BASEDIR: " + KTR_CONF.basedir, 0)
log("ktr: CONFDIR: " + KTR_CONF.confdir, 0)
log("ktr: DATADIR: " + KTR_CONF.datadir, 0)
log("ktr: PACKDIR: " + KTR_CONF.packdir, 0)
log("ktr: SPECDIR: " + KTR_CONF.specdir, 0)

