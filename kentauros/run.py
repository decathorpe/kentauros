"""
This module contains the :py:func:`run` function that is called as entry point from the `ktr`
script.
"""


import glob
import os

from kentauros.definitions import ActionType

from kentauros.instance import Kentauros

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.package import Package


LOGPREFIX = "ktr"
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def run():
    """
    This function is corresponding to (one of) the "main" function of the `kentauros` package and is
    the entry point used by the ``ktr`` script from git and the script installed by setuptools at
    installation.
    """

    ktr = Kentauros(LOGPREFIX)

    print()

    ktr.log("DEBUG set: " + str(ktr.debug), 0)
    ktr.log("VERBOSITY: " + str(ktr.verby) + "/2", 1)

    ktr.dbg("BASEDIR: " + ktr.conf.basedir)
    ktr.dbg("CONFDIR: " + ktr.conf.get_confdir())
    ktr.dbg("DATADIR: " + ktr.conf.get_datadir())
    ktr.dbg("EXPODIR: " + ktr.conf.get_expodir())
    ktr.dbg("PACKDIR: " + ktr.conf.get_packdir())
    ktr.dbg("SPECDIR: " + ktr.conf.get_specdir())

    print()

    # if no action is specified: exit
    if ktr.cli.get_action() == ActionType.NONE:
        ktr.log("No action specified. Exiting.")
        ktr.log("Use 'ktr --help' for more information.")
        print()
        return

    if not ktr_bootstrap():
        raise SystemExit()

    pkgs = list()

    # if only specified packages are to be processed: process packages from CLI only
    if not ktr.cli.get_packages_all():
        pkgs = ktr.cli.get_packages().copy()

        for pkg in pkgs:
            pkg_conf_path = os.path.join(ktr.conf.get_confdir(), pkg + ".conf")

            if not os.path.exists(pkg_conf_path):
                ktr.err("Package configuration for '" + pkg + "' could not be found.")
                pkgs.remove(pkg)

    # if all package are to be processed: get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(ktr.conf.get_confdir(), "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).replace(".conf", ""))

    if not pkgs:
        ktr.log("No packages have been specified or found. Exiting.")
        print()
        raise SystemExit()

    # log list of found packages
    ktr.log_list("Packages", pkgs)
    print()

    # generate package objects
    for name in pkgs:
        assert isinstance(name, str)

        ktr.add_package(name, Package(name))

    action_succ = list()
    action_fail = list()

    # run action for every specified package
    for name in ktr.get_package_names():
        assert isinstance(name, str)

        action_type = ktr.cli.get_action()
        action = ACTION_DICT[action_type](name)
        success = action.execute()

        if success:
            ktr.log(name + ": Success!")
            action_succ.append(name)
        else:
            ktr.log(name + ": Not successful.")
            action_fail.append(name)

    print()

    if action_succ:
        ktr.log_list("Successful actions", action_succ)

    if action_fail:
        ktr.log_list("Failed actions", action_fail)

    print()

    raise SystemExit()
