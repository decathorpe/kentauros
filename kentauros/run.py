"""
This module contains the :py:func:`run` function that is called as entry point from the `ktr`
script.
"""


import glob
import os

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger, print_flush

from kentauros.actions import ACTION_DICT, ImportAction
from kentauros.bootstrap import ktr_bootstrap
from kentauros.package import Package, PackageError


LOGPREFIX = "ktr"
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def print_parameters():
    """
    This function prints the general execution parameters.
    """

    ktr = Kentauros()
    logger = KtrLogger(LOGPREFIX)

    print_flush()

    logger.log("Debugging:                          " + str(ktr.debug), 0)
    logger.log("Logger Verbosity:                   " + str(ktr.verby) + "/2", 1)

    print_flush()

    logger.dbg("Base directory:                     " + ktr.conf.basedir)
    logger.dbg("Package configuration directory:    " + ktr.conf.get_confdir())
    logger.dbg("Package sources directory:          " + ktr.conf.get_datadir())
    logger.dbg("Binary package directory:           " + ktr.conf.get_expodir())
    logger.dbg("Source package directory:           " + ktr.conf.get_packdir())
    logger.dbg("Package specification directory:    " + ktr.conf.get_specdir())

    print_flush()


def run():
    """
    This function is corresponding to (one of) the "main" function of the `kentauros` package and is
    the entry point used by the `ktr.py` script from git and the script installed at installation.
    """

    ktr = Kentauros()
    logger = KtrLogger(LOGPREFIX)

    # if no action is specified: exit
    if ktr.cli.get_action() is None:
        logger.log("No action specified. Exiting.")
        logger.log("Use 'ktr --help' for more information.")
        print_flush()
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
                logger.err("Package configuration for '" + pkg + "' could not be found.")
                pkgs.remove(pkg)

    # if all package are to be processed: get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(ktr.conf.get_confdir(), "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).replace(".conf", ""))

    if not pkgs:
        logger.log("No packages have been specified or found. Exiting.")
        print_flush()
        raise SystemExit()

    pkgs.sort()

    # log list of found packages
    logger.log_list("Packages", pkgs)
    print_flush()

    # generate package objects
    for name in pkgs:
        assert isinstance(name, str)

        try:
            pkg = Package(name)
            ktr.add_package(name, pkg)
        except PackageError:
            logger.log("Package with configuration file '" + name + "' is invalid, skipping.")
            continue

    action_succ = list()
    action_fail = list()

    # run action for every specified package
    for name in ktr.get_package_names():
        assert isinstance(name, str)

        if ktr.state_read(name) is None:
            logger.log("Importing new package into the database.")
            import_action = ImportAction(name)
            import_action.execute()

        action_type = ktr.cli.get_action()
        action = ACTION_DICT[action_type](name)
        success = action.execute()

        if success:
            logger.log(name + ": Success!")
            action_succ.append(name)
        else:
            logger.log(name + ": Not successful.")
            action_fail.append(name)

    print_flush()

    if action_succ:
        logger.log_list("Successful actions", action_succ)

    if action_fail:
        logger.log_list("Failed actions", action_fail)

    print_flush()

    raise SystemExit()
