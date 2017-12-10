"""
This module contains the :py:func:`run` function that is called as entry point from the `ktr`
script.
"""


import glob
import os

from .actions import ImportAction, VerifyAction, get_action
from .bootstrap import ktr_bootstrap
from .definitions import ActionType
from .instance import Kentauros
from .logcollector import LogCollector
from .package import Package, PackageError
from .result import KtrResult


def print_parameters(logger: LogCollector):
    """
    This function prints the kentauros program parameters.
    """

    ktr = Kentauros()

    if ktr.debug or ktr.verby < 2:
        logger.log("\n")

    logger.log("Debugging:                          " + str(ktr.debug))
    logger.log("Logger Verbosity:                   " + str(ktr.verby) + "/2")

    if ktr.debug:
        logger.log("\n")

    logger.dbg("Base directory:                     " + ktr.get_basedir())
    logger.dbg("Package configuration directory:    " + ktr.get_confdir())
    logger.dbg("Package sources directory:          " + ktr.get_datadir())
    logger.dbg("Binary package directory:           " + ktr.get_expodir())
    logger.dbg("Source package directory:           " + ktr.get_packdir())
    logger.dbg("Package specification directory:    " + ktr.get_specdir())

    logger.log("\n")


def print_no_package_error(logger: LogCollector):
    """
    This function prints an error and helpful information if no action is specified.
    """

    logger.log("No action specified. Exiting.")
    logger.log("Use 'ktr --help' for more information.")

    logger.log("\n")


def get_packages_cli() -> list:
    """
    This function parses the package configuration names supplied via CLI arguments, removes any
    that do not match with a present configuration file in the respective directory, and returns
    the checked list.

    Returns:
        list:       list of strings of package configuration names
    """

    ktr = Kentauros()

    packages = list()

    for pkg in ktr.cli.get_packages():
        pkg_conf_path = os.path.join(ktr.get_confdir(), pkg + ".conf")

        if os.path.exists(pkg_conf_path):
            packages.append(pkg)
        else:
            raise PackageError("Package configuration for '" + pkg + "' could not be found.")

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


def init_package_objects(packages: list, logger: LogCollector):
    """
    This function parses the list of package configuration names and initialises the `Package`
    objects. If no errors occur during initialisation, the `Package` instance is added to the
    kentauros instance's list of packages.
    """

    ktr = Kentauros()

    for name in packages:
        assert isinstance(name, str)

        try:
            pkg = Package(name)
        except PackageError as error:
            logger.log("Invalid package configuration file:")
            logger.log(error.value)
            continue

        ktr.add_package(name, pkg)


def print_package_header(name: str, logger: LogCollector):
    """
    This function prints a small banner to indicate which package actions are executed for next.

    Arguments:
        str name:   package configuration name
    """

    assert isinstance(name, str)

    logger.log("------------------------------" + "-" * len(name))
    logger.log("Executing actions on package: " + name)
    logger.log("------------------------------" + "-" * len(name))


def do_import_action(name: str, logger: LogCollector):
    """
    This function executes the Import action for the given package configuration.

    Arguments:
        str name:   package configuration name
    """

    assert isinstance(name, str)

    logger.log("Importing new package '" + name + "' into the database.")
    import_action = ImportAction(name)
    import_action.execute()


def do_verify_action(name: str, logger: LogCollector) -> bool:
    """
    This function executes the Verify action for the given package configuration.

    Arguments:
        str name:   package configuration name
    """

    assert isinstance(name, str)

    logger.dbg("Verifying package '" + name + "'.")
    verification = VerifyAction(name)

    res = verification.execute()
    logger.merge(res.messages)

    return res.success


def do_process_packages(logger: LogCollector) -> (list, list):
    """
    This function processes all packages and executes the specified action on them.

    Returns:
        list, list:     list of successful package actions, list of unsuccessful package actions
    """

    ktr = Kentauros()

    actions_success = list()
    actions_failure = list()

    # run action for every specified package
    for name in ktr.get_package_names():
        assert isinstance(name, str)

        action_type = ktr.cli.get_action()

        print_package_header(name, logger)

        if ktr.state_read(name) is None:
            do_import_action(name, logger)

        verified = do_verify_action(name, logger)

        if action_type == ActionType.VERIFY:
            if verified:
                logger.log("Package successfully verified.")
                actions_success.append(name)
            else:
                logger.log("Package did not pass verification.")
                actions_failure.append(name)

            logger.log("\n")
            continue

        else:
            if verified:
                logger.dbg("Package successfully verified.")
            else:
                logger.log("Package configuration file is invalid, skipping package.")
                actions_failure.append(name)

                logger.log("\n")
                continue

        action = get_action(action_type, name)
        res: KtrResult = action.execute()
        logger.merge(res.messages)

        logger.log("\n")

        if res.success:
            actions_success.append(name)
        else:
            actions_failure.append(name)

    return actions_success, actions_failure


def run() -> int:
    """
    This function is corresponding to (one of) the "main" function of the `kentauros` package and is
    the entry point used by the `ktr.py` script from git and the script installed at installation.
    """

    ktr = Kentauros()
    logger = LogCollector()

    try:
        print_parameters(logger)

        # if no action is specified: exit(0)
        if ktr.cli.get_action() == ActionType.NONE:
            print_no_package_error(logger)
            return 0

        # initialise directory structure and exit(1) if it fails
        if not ktr_bootstrap(logger):
            return 1

        # get packages from CLI (all or specific ones)
        packages = get_packages()

        # if no package configurations are found: exit(0)
        if not packages:
            logger.log("No packages have been specified or found. Exiting.")
            logger.log("\n")
            return 0

        # log list of found packages
        logger.lst("Packages", packages)
        logger.log("\n")

        # generate package objects
        init_package_objects(packages, logger)

        # execute package actions
        actions_success, actions_failure = do_process_packages(logger)

        # print execution success
        if actions_success:
            logger.lst("Successful actions", actions_success)

        if actions_failure:
            logger.lst("Failed actions", actions_failure)

        logger.log("\n")
    finally:
        logger.print(warnings=True, debug=ktr.debug)

    return 0
