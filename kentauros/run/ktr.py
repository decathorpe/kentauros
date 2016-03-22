"""
# TODO: napoleon docstring
this file contains the run() function called by 'ktr' as entry point
"""

import glob
import os

from kentauros.definitions import InstanceType
from kentauros.instance import Kentauros, dbg, log

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.run.common import get_action_args


LOGPREFIX1 = "ktr: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = "     - "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


def run():
    # TODO: napoleon docstring
    "will be run if executed by 'ktr' script # TODO: napoleon docstring"

    ktr = Kentauros(itype=InstanceType.NORMAL)

    print()

    log(LOGPREFIX1 + "DEBUG set: " + str(ktr.debug), 0)
    log(LOGPREFIX1 + "VERBOSITY: " + str(ktr.verby) + "/2", 1)

    dbg(LOGPREFIX1 + "BASEDIR: " + ktr.conf.basedir)
    dbg(LOGPREFIX1 + "CONFDIR: " + ktr.conf.confdir)
    dbg(LOGPREFIX1 + "DATADIR: " + ktr.conf.datadir)
    dbg(LOGPREFIX1 + "PACKDIR: " + ktr.conf.packdir)
    dbg(LOGPREFIX1 + "SPECDIR: " + ktr.conf.specdir)

    # if no action is specified: exit
    if ktr.cli.action is None:
        log(LOGPREFIX1 + "No action specified. Exiting.", 2)
        log(LOGPREFIX1 + "Use 'ktr --help' for more information.")
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
    log(LOGPREFIX1 + "Packages:", 2)
    for package in pkgs:
        log(LOGPREFIX2 + package, 2)

    # run action for every specified package
    for name in pkgs:
        action_type = ktr.cli.action
        action = ACTION_DICT[action_type](*get_action_args(ktr.cli,
                                                           name,
                                                           action_type))
        success = action.execute()

        if success:
            log(LOGPREFIX1 + name + ": Success!")
        else:
            log(LOGPREFIX1 + name + ": Not successful.")

    print()

