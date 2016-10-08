"""
This module contains the :py:func:`run_config` function that is called as entry
point from the ``ktr-config`` script.
"""

import glob
import os

from kentauros.definitions import ActionType, InstanceType
from kentauros.instance import Kentauros, dbg, log

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.run.common import get_action_args


LOGPREFIX1 = "ktr-config: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = "            - "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


def run_config():
    """
    This function is corresponding to (one of) the "main" function of the
    `kentauros` package and is the entry point used by the ``ktr-config`` script
    from git and the script installed by setuptools at installation.
    """

    ktr = Kentauros(itype=InstanceType.CONFIG)

    print(flush=True)

    log(LOGPREFIX1 + "DEBUG set: " + str(ktr.debug), 0)
    log(LOGPREFIX1 + "VERBOSITY: " + str(ktr.verby) + "/2", 1)

    dbg(LOGPREFIX1 + "BASEDIR: " + ktr.conf.basedir)
    dbg(LOGPREFIX1 + "CONFDIR: " + ktr.conf.confdir)
    dbg(LOGPREFIX1 + "DATADIR: " + ktr.conf.datadir)
    dbg(LOGPREFIX1 + "PACKDIR: " + ktr.conf.packdir)
    dbg(LOGPREFIX1 + "SPECDIR: " + ktr.conf.specdir)

    if not ktr_bootstrap():
        raise SystemExit

    pkgs = list()

    # if only specified packages are to be processed:
    # process packages only
    if not ktr.cli.get_packages_all():
        for name in ktr.cli.get_packages():
            pkgs.append(name)

    # if all package are to be processed:
    # get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(
            ktr.conf.confdir, "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).replace(".conf", ""))

    # log list of found packages
    log(LOGPREFIX1 + "Packages:", 2)
    for package in pkgs:
        log(LOGPREFIX2 + package, 2)

    # run action for every specified package
    for name in pkgs:
        action = ACTION_DICT[ActionType.CONFIG](
            *get_action_args(ktr.cli, name, ActionType.CONFIG))
        success = action.execute()

        if success:
            log(LOGPREFIX1 + name + ": Success!")
        else:
            log(LOGPREFIX1 + name + ": Not successful.")

    print(flush=True)

