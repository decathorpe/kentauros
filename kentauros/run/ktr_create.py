"""
This module contains the :py:func:`run_create` function that is called as entry
point from the ``ktr-create`` script.
"""


from kentauros.definitions import ActionType, InstanceType
from kentauros.instance import Kentauros, dbg, log

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.run.common import get_action_args


LOGPREFIX1 = "ktr-create: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = "            - "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


def run_create():
    "will be run if executed by 'ktr-create' script"
    # TODO: napoleon function docstring

    ktr = Kentauros(itype=InstanceType.CREATE)

    print()

    log(LOGPREFIX1 + "DEBUG set: " + str(ktr.debug), 0)
    log(LOGPREFIX1 + "VERBOSITY: " + str(ktr.verby) + "/2", 1)

    dbg(LOGPREFIX1 + "BASEDIR: " + ktr.conf.basedir)
    dbg(LOGPREFIX1 + "CONFDIR: " + ktr.conf.confdir)
    dbg(LOGPREFIX1 + "DATADIR: " + ktr.conf.datadir)
    dbg(LOGPREFIX1 + "PACKDIR: " + ktr.conf.packdir)
    dbg(LOGPREFIX1 + "SPECDIR: " + ktr.conf.specdir)

    ktr_bootstrap()

    # get packages from CLI
    pkgs = ktr.cli.get_packages()

    # if list of packages is empty, nothing has to be done
    if not pkgs:
        log(LOGPREFIX1 + "No package names given. Exiting.", 2)
        print()
        return

    # log list of found packages
    log(LOGPREFIX1 + "Packages:", 2)
    for package in pkgs:
        log(LOGPREFIX2 + package, 2)

    # run action for every specified package
    for name in pkgs:
        action = ACTION_DICT[ActionType.CREATE](
            *get_action_args(ktr.cli, name, ActionType.CREATE))
        success = action.execute()

        if success:
            log(LOGPREFIX1 + name + ": Success!")
        else:
            log(LOGPREFIX1 + name + ": Not successful.")

    print()

