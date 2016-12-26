"""
This module contains the :py:func:`run` function that is called as entry point from the `ktr`
script.
"""


import glob
import os

from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger, print_flush

from kentauros.actions import ACTION_DICT, ImportAction
from kentauros.bootstrap import ktr_bootstrap
from kentauros.package import Package, PackageError


LOG_PREFIX = "ktr"
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def print_parameters():
    """
    This function prints the general execution parameters.
    """

    ktr = Kentauros()
    logger = KtrLogger(LOG_PREFIX)

    if ktr.debug or ktr.verby < 2:
        print_flush()

    logger.log("Debugging:                          " + str(ktr.debug), 0)
    logger.log("Logger Verbosity:                   " + str(ktr.verby) + "/2", 1)

    if ktr.debug:
        print_flush()

    logger.dbg("Base directory:                     " + ktr.get_basedir())
    logger.dbg("Package configuration directory:    " + ktr.get_confdir())
    logger.dbg("Package sources directory:          " + ktr.get_datadir())
    logger.dbg("Binary package directory:           " + ktr.get_expodir())
    logger.dbg("Source package directory:           " + ktr.get_packdir())
    logger.dbg("Package specification directory:    " + ktr.get_specdir())

    print_flush()


def run() -> int:
    """
    This function is corresponding to (one of) the "main" function of the `kentauros` package and is
    the entry point used by the `ktr.py` script from git and the script installed at installation.
    """

    ktr = Kentauros()
    logger = KtrLogger(LOG_PREFIX)

    print_parameters()

    # if no action is specified: exit
    if ktr.cli.get_action() == ActionType.NONE:
        logger.log("No action specified. Exiting.")
        logger.log("Use 'ktr --help' for more information.")
        print_flush()
        return 0

    if not ktr_bootstrap():
        return 1

    packages = list()

    # if only specified packages are to be processed: process packages from CLI only
    if not ktr.cli.get_packages_all():
        packages = ktr.cli.get_packages().copy()

        for pkg in packages:
            pkg_conf_path = os.path.join(ktr.get_confdir(), pkg + ".conf")

            if not os.path.exists(pkg_conf_path):
                logger.err("Package configuration for '" + pkg + "' could not be found.")
                packages.remove(pkg)

    # if all package are to be processed: get package configs present in the package configuration
    # directory
    else:
        pkg_conf_paths = glob.glob(os.path.join(ktr.get_confdir(), "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            packages.append(os.path.basename(pkg_conf_path).replace(".conf", ""))

    if not packages:
        logger.log("No packages have been specified or found. Exiting.")
        print_flush()
        return 0

    packages.sort()

    # log list of found packages
    logger.log_list("Packages", packages)
    print_flush()

    # generate package objects
    for name in packages:
        assert isinstance(name, str)

        try:
            pkg = Package(name)
            ktr.add_package(name, pkg)
        except PackageError:
            logger.log("Package with configuration file '" + name + "' is invalid, skipping.")
            continue

    actions_success = list()
    actions_failure = list()

    # run action for every specified package
    for name in ktr.get_package_names():
        assert isinstance(name, str)

        if ktr.state_read(name) is None:
            logger.log("Importing new package '" + name + "' into the database.")
            import_action = ImportAction(name)
            import_action.execute()

        action_type = ktr.cli.get_action()
        action = ACTION_DICT[action_type](name)
        success = action.execute()

        if success:
            actions_success.append(name)
        else:
            actions_failure.append(name)

    print_flush()

    if actions_success:
        logger.log_list("Successful actions", actions_success)

    if actions_failure:
        logger.log_list("Failed actions", actions_failure)

    print_flush()

    return 0
