"""
this file contains the run_config() function called by 'ktr_config'
as entry point
"""

import glob
import os

from kentauros.definitions import ActionType, InstanceType
from kentauros.instance import Kentauros, dbg, log

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.run.common import get_action_args


def run_config():
    "will be run if executed by 'ktr-config' script"
    log_prefix1 = "ktr-config: "
    log_prefix2 = "            - "

    ktr = Kentauros(itype=InstanceType.CONFIG)

    print()

    log(log_prefix1 + "DEBUG set: " + str(ktr.debug), 0)
    log(log_prefix1 + "VERBOSITY: " + str(ktr.verby) + "/2", 1)

    dbg(log_prefix1 + "BASEDIR: " + ktr.conf.basedir)
    dbg(log_prefix1 + "CONFDIR: " + ktr.conf.confdir)
    dbg(log_prefix1 + "DATADIR: " + ktr.conf.datadir)
    dbg(log_prefix1 + "PACKDIR: " + ktr.conf.packdir)
    dbg(log_prefix1 + "SPECDIR: " + ktr.conf.specdir)

    if (ktr.cli.action is not None) and ktr.cli.action != ActionType.CONFIG:
        log(log_prefix1 + "ktr-config does not take action arguments.", 2)

    ktr.cli.action = ActionType.CONFIG

    ktr_bootstrap()

    pkgs = list()

    # if only specified packages are to be processed:
    # process packages only
    if not ktr.cli.packages_all:
        for name in ktr.cli.packages:
            pkgs.append(name)

    # if all package are to be processed:
    # get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(
            ktr.conf.confdir, "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).rstrip(".conf"))

    # log list of found packages
    log(log_prefix1 + "Packages:", 2)
    for package in pkgs:
        log(log_prefix2 + package, 2)

    # run action for every specified package
    for name in pkgs:
        action = ACTION_DICT[ActionType.CONFIG](
            *get_action_args(ktr.cli, name, ActionType.CONFIG))
        success = action.execute()

        if success:
            log(log_prefix1 + name + ": Success!")
        else:
            log(log_prefix1 + name + ": Not successful.")

    print()
