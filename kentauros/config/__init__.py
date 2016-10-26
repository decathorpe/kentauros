"""
This subpackage contains definitions of the default kentauros configuration files' locations, error
messages if they are not found, and a function that returns the configuration values determined from
the highest priority configuration found or the configuration location specified at command line.
"""


from collections import OrderedDict
import os

from kentauros.definitions import KTR_SYSTEM_DATADIR

from kentauros.config.cli import get_cli_config
from kentauros.config.envvar import get_env_config
from kentauros.config.fallback import get_fallback_config

from kentauros.config.common import KtrConf
from kentauros.definitions import KtrConfType

from kentauros.init.cli import CLIArgs
from kentauros.init.env import get_env_home


def get_conf_from_file_args(conf_type: KtrConfType) -> tuple:
    """
    This function returns the arguments for :py:meth:`KtrConf.from_file` method calls, depending
    on the type of configuration file location.

    Arguments:
        KtrConfType conf_type: type of configuration arguments will be built for

    Returns:
        tuple: collection of method call arguments
    """

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


def ktr_get_conf() -> KtrConf:
    """
    This function gets and parses :py:class:`KtrConf` instances for configuration values.

    Returns:
        KtrConf:  highest-priority or requested :py:class:`KtrConf` instance
    """

    # configurations, in ascending priority
    ktr_configs = OrderedDict()

    def_config = KtrConf(KtrConfType.DEF).from_file(*get_conf_from_file_args(KtrConfType.DEF))
    sys_config = KtrConf(KtrConfType.SYS).from_file(*get_conf_from_file_args(KtrConfType.SYS))
    usr_config = KtrConf(KtrConfType.USR).from_file(*get_conf_from_file_args(KtrConfType.USR))
    prj_config = KtrConf(KtrConfType.PRJ).from_file(*get_conf_from_file_args(KtrConfType.PRJ))

    ktr_configs[KtrConfType.FBK] = get_fallback_config()
    ktr_configs[KtrConfType.DEF] = def_config
    ktr_configs[KtrConfType.SYS] = sys_config
    ktr_configs[KtrConfType.USR] = usr_config
    ktr_configs[KtrConfType.PRJ] = prj_config
    ktr_configs[KtrConfType.ENV] = get_env_config()
    ktr_configs[KtrConfType.CLI] = get_cli_config()

    ktr_conf = None

    cli_args = CLIArgs()

    if cli_args.get_priconf():
        ktr_conf = ktr_configs[cli_args.get_priconf()]

    if ktr_conf is not None:
        return ktr_conf

    # KTR_CONF should contain the highest-priority,
    # non-None configuration for every value
    ktr_conf = ktr_configs[KtrConfType.FALLBACK]

    for conf_type in ktr_configs:
        # skip FALLBACK config
        if conf_type == KtrConfType.FALLBACK:
            continue

        conf = ktr_configs[conf_type]
        if conf is not None:
            ktr_conf.succby(conf)

    return ktr_conf
