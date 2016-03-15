"""
this file contains the run() function called by 'ktr' as entry point
"""

import glob
import os

from kentauros.definitions import InstanceType
from kentauros.instance import Kentauros, dbg, log

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.run.common import get_action_args


def run():
    "will be run if executed by 'ktr' script"
    log_prefix1 = "ktr: "
    log_prefix2 = "     - "

    ktr = Kentauros(itype=InstanceType.NORMAL)

    print()

    log(log_prefix1 + "DEBUG set: " + str(ktr.debug), 0)
    log(log_prefix1 + "VERBOSITY: " + str(ktr.verby) + "/2", 1)

    dbg(log_prefix1 + "BASEDIR: " + ktr.conf.basedir)
    dbg(log_prefix1 + "CONFDIR: " + ktr.conf.confdir)
    dbg(log_prefix1 + "DATADIR: " + ktr.conf.datadir)
    dbg(log_prefix1 + "PACKDIR: " + ktr.conf.packdir)
    dbg(log_prefix1 + "SPECDIR: " + ktr.conf.specdir)

    # if no action is specified: exit
    if ktr.cli.action is None:
        log(log_prefix1 + "No action specified. Exiting.", 2)
        log(log_prefix1 + "Use 'ktr --help' for more information.")
        print()
        return

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
        action_type = ktr.cli.action
        action = ACTION_DICT[action_type](*get_action_args(ktr.cli,
                                                           name,
                                                           action_type))
        success = action.execute()

        if success:
            log(log_prefix1 + name + ": Success!")
        else:
            log(log_prefix1 + name + ": Not successful.")

    print()

