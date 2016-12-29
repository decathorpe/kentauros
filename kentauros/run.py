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
    This function prints the kentauros program parameters.
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


def get_packages_cli() -> list:
    """
    This function parses the package configuration names supplied via CLI arguments, removes any
    that do not match with a present configuration file in the respective directory, and returns
    the checked list.

    Returns:
        list:       list of strings of package configuration names
    """

    ktr = Kentauros()
    logger = KtrLogger(LOG_PREFIX)

    packages = list()

    for pkg in ktr.cli.get_packages():
        pkg_conf_path = os.path.join(ktr.get_confdir(), pkg + ".conf")

        if os.path.exists(pkg_conf_path):
            packages.append(pkg)
        else:
            logger.err("Package configuration for '" + pkg + "' could not be found.")

    packages.sort()

    return packages


def get_packages_all() -> list:
    """
    This function parses the content of the package configuration files directory and returns the
    package configuration names.

    Returns:
        list:       list of strings of package configuration names
    """

    ktr = Kentauros()

    packages = list()

    pkg_conf_paths = glob.glob(os.path.join(ktr.get_confdir(), "*.conf"))

    for pkg_conf_path in pkg_conf_paths:
        packages.append(os.path.basename(pkg_conf_path).replace(".conf", ""))

    packages.sort()

    return packages


def get_packages() -> list:
    """
    This function returns the set of all packages that are specified as command line arguments or
    all packages that have configuration files present, depending on whether the `--all` CLI flag
    has been set.

    Returns:
        list:       list of package configuration names
    """

    ktr = Kentauros()

    # if only specified packages are to be processed:
    # process packages from CLI only
    if not ktr.cli.get_packages_all():
        packages = get_packages_cli()

    # if all package are to be processed:
    # get package configs present in the package configuration directory
    else:
        packages = get_packages_all()

    return packages


def init_package_objects(packages: list):
    """
    This function parses the list of package configuration names and initialises the `Package`
    objects. If no errors occur during initialisation, the `Package` instance is added to the
    kentauros instance's list of packages.
    """

    ktr = Kentauros()
    logger = KtrLogger(LOG_PREFIX)

    for name in packages:
        assert isinstance(name, str)

        try:
            pkg = Package(name)
        except PackageError:
            logger.log("Package with configuration file '" + name + "' is invalid, skipping.")
            continue

        ktr.add_package(name, pkg)


def run() -> int:
    """
    This function is corresponding to (one of) the "main" function of the `kentauros` package and is
    the entry point used by the `ktr.py` script from git and the script installed at installation.
    """

    ktr = Kentauros()
    logger = KtrLogger(LOG_PREFIX)

    print_parameters()

    # if no action is specified: exit(0)
    if ktr.cli.get_action() == ActionType.NONE:
        logger.log("No action specified. Exiting.")
        logger.log("Use 'ktr --help' for more information.")
        print_flush()
        return 0

    # initialise directory structure and exit(1) if it fails
    if not ktr_bootstrap():
        return 1

    # get packages from CLI (all or specific ones)
    packages = get_packages()

    # if no package configurations are found: exit(0)
    if not packages:
        logger.log("No packages have been specified or found. Exiting.")
        print_flush()
        return 0

    # log list of found packages
    logger.log_list("Packages", packages)
    print_flush()

    # generate package objects
    init_package_objects(packages)

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

        print_flush()

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
