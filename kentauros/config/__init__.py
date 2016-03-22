"""
This subpackage contains definitions of the default kentauros configuration
files' locations, error messages if they are not found, and a function that
returns the configuration values determined from the highest priority
configuration found or the configuration location specified at command line.
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

from kentauros.init.cli import CLIArgs
from kentauros.init.env import get_env_home


__all__ = ["cli", "common", "envvar", "fallback"]


LOGPREFIX1 = "ktr/config: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = "            - "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


def _get_conf_from_file_args(conf_type):
    assert isinstance(conf_type, KtrConfType)

    def_file_path = os.path.join(KTR_SYSTEM_DATADIR, "default.conf")
    prj_file_path = os.path.abspath("./kentaurosrc")
    sys_file_path = "/etc/kentaurosrc"
    usr_file_path = os.path.join(get_env_home(), ".config/kentaurosrc")

    def_err_msg = def_file_path + " does not exist or it is not readable."
    prj_err_msg = "This directory does not contain a readable kentaurosrc file."
    sys_err_msg = sys_file_path + " does not exist or is not readable."
    usr_err_msg = usr_file_path + " does not exist or is not readable."

    conf_from_file_args = dict()
    conf_from_file_args[KtrConfType.DEF] = (def_file_path, def_err_msg)
    conf_from_file_args[KtrConfType.PRJ] = (prj_file_path, prj_err_msg)
    conf_from_file_args[KtrConfType.SYS] = (sys_file_path, sys_err_msg)
    conf_from_file_args[KtrConfType.USR] = (usr_file_path, usr_err_msg)

    return conf_from_file_args[conf_type]


def ktr_get_conf():
    """
    # TODO: napoleon docstring
    kentauros.config.get_conf()
    get and return highest-priority configuration for every config value
    """

    def get_pref_conf(conf_dict, pref_conf):
        """
        kentauros.config.get_pref_conf()
        get and return preferred-by-CLI configuration
        """

        # check if requirested config type is in Enum
        # pylint: disable=unsubscriptable-object

        # get requested config from Dict
        if pref_conf:
            return conf_dict[pref_conf]
        else:
            return None


    # configurations, in ascending priority
    ktr_confs = OrderedDict()

    def_config = KtrConf(KtrConfType.DEF).from_file(
        *_get_conf_from_file_args(KtrConfType.DEF))
    sys_config = KtrConf(KtrConfType.SYS).from_file(
        *_get_conf_from_file_args(KtrConfType.SYS))
    usr_config = KtrConf(KtrConfType.USR).from_file(
        *_get_conf_from_file_args(KtrConfType.USR))
    prj_config = KtrConf(KtrConfType.PRJ).from_file(
        *_get_conf_from_file_args(KtrConfType.PRJ))

    ktr_confs[KtrConfType.FBK] = get_fallback_config()
    ktr_confs[KtrConfType.DEF] = def_config
    ktr_confs[KtrConfType.SYS] = sys_config
    ktr_confs[KtrConfType.USR] = usr_config
    ktr_confs[KtrConfType.PRJ] = prj_config
    ktr_confs[KtrConfType.ENV] = get_env_config()
    ktr_confs[KtrConfType.CLI] = get_cli_config()


    ktr_conf = None

    cli_args = CLIArgs()

    if cli_args.priconf:
        ktr_conf = get_pref_conf(ktr_confs, cli_args.priconf)

    if ktr_conf is not None:
        return ktr_conf

    # KTR_CONF should contain the highest-priority,
    # non-None configuration for every value
    ktr_conf = ktr_confs[KtrConfType.FALLBACK]

    for conftype in ktr_confs:
        # skip FALLBACK config
        if conftype == KtrConfType.FALLBACK:
            continue

        conf = ktr_confs[conftype]
        if conf is not None:
            ktr_conf.succby(conf)

    return ktr_conf

