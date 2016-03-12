"""
This module contains the 'run' main function that is called when the
package is executed by the setuptools-installed 'ktr' script.
"""


import glob
import os

from kentauros.actions import ACTION_DICT
from kentauros.definitions import ActionType, InstanceType

from kentauros.init import get_debug, get_verby, log, dbg
from kentauros.init.cli import CLIArgs, get_parsed_cli

from kentauros.config import ktr_get_conf
from kentauros.bootstrap import ktr_bootstrap

from kentauros.package import Package


def get_action_args(cli_args, pkgname, action_type_enum):
    """
    This function returns arguments for an Action() constructor as tuple.
    It only constructs Package() objects as needed.

    Arguments:
        cli_args (CLIArgs): parsed command line arguments
        pkgname (str): name of package the action will be executed for
        action_type_enum (ActionType): specifies the type of Action

    Returns:
        tuple: :py:class:`kentauros.action.Action` Constructor arguments
    """

    assert isinstance(action_type_enum, ActionType)

    action_args_dict = dict()
    action_args_dict[ActionType.BUILD] = (cli_args.force,)
    action_args_dict[ActionType.CHAIN] = (cli_args.force,)
    action_args_dict[ActionType.CLEAN] = (cli_args.force,)
    action_args_dict[ActionType.CONSTRUCT] = (cli_args.force,)
    action_args_dict[ActionType.EXPORT] = (cli_args.force,)
    action_args_dict[ActionType.GET] = (cli_args.force,)
    action_args_dict[ActionType.REFRESH] = (cli_args.force,)
    action_args_dict[ActionType.STATUS] = (cli_args.force,)
    action_args_dict[ActionType.UPDATE] = (cli_args.force,)
    action_args_dict[ActionType.UPLOAD] = (cli_args.force,)
    action_args_dict[ActionType.VERIFY] = (cli_args.force,)

    if action_type_enum == ActionType.CONFIG:
        action_args_dict[ActionType.CONFIG] = (cli_args.force,
                                               cli_args.config_section,
                                               cli_args.config_key,
                                               cli_args.config_value)

    action_args_dict[ActionType.CREATE] = (cli_args.force,)

    if action_type_enum == ActionType.CREATE:
        return (pkgname,) + action_args_dict[ActionType.CREATE]
    else:
        return (Package(pkgname),) + action_args_dict[action_type_enum]


def run():
    "will be run if executed by 'ktr' script"
    log_prefix1 = "ktr: "
    log_prefix2 = "     - "

    print()

    log(log_prefix1 + "DEBUG set: " + str(get_debug()), 0)
    log(log_prefix1 + "VERBOSITY: " + str(get_verby()) + "/2", 1)

    dbg(log_prefix1 + "BASEDIR: " + ktr_get_conf().basedir)
    dbg(log_prefix1 + "CONFDIR: " + ktr_get_conf().confdir)
    dbg(log_prefix1 + "DATADIR: " + ktr_get_conf().datadir)
    dbg(log_prefix1 + "PACKDIR: " + ktr_get_conf().packdir)
    dbg(log_prefix1 + "SPECDIR: " + ktr_get_conf().specdir)

    cli_args = CLIArgs()
    cli_args.parse_args(get_parsed_cli())

    # if no action is specified: exit
    if cli_args.action is None:
        log(log_prefix1 + "No action specified. Exiting.", 2)
        log(log_prefix1 + "Use 'ktr --help' for more information.")
        print()
        return

    ktr_bootstrap()

    pkgs = list()

    # if only specified packages are to be processed:
    # process packages only
    if not cli_args.packages_all:
        for name in cli_args.packages:
            pkgs.append(name)

    # if all package are to be processed:
    # get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(
            ktr_get_conf().confdir, "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).rstrip(".conf"))

    # log list of found packages
    log(log_prefix1 + "Packages:", 2)
    for package in pkgs:
        log(log_prefix2 + package, 2)

    # run action for every specified package
    for name in pkgs:
        action_type = cli_args.action
        action = ACTION_DICT[action_type](*get_action_args(cli_args,
                                                           name,
                                                           action_type))
        success = action.execute()

        if success:
            log(log_prefix1 + name + ": Success!")
        else:
            log(log_prefix1 + name + ": Not successful.")

    print()


def run_config():
    "will be run if executed by 'ktr-config' script"
    log_prefix1 = "ktr-config: "
    log_prefix2 = "            - "

    print()

    log(log_prefix1 + "DEBUG set: " + str(get_debug()), 0)
    log(log_prefix1 + "VERBOSITY: " + str(get_verby()) + "/2", 1)

    dbg(log_prefix1 + "BASEDIR: " + ktr_get_conf().basedir)
    dbg(log_prefix1 + "CONFDIR: " + ktr_get_conf().confdir)
    dbg(log_prefix1 + "DATADIR: " + ktr_get_conf().datadir)
    dbg(log_prefix1 + "PACKDIR: " + ktr_get_conf().packdir)
    dbg(log_prefix1 + "SPECDIR: " + ktr_get_conf().specdir)

    cli_args = CLIArgs(instance_type=InstanceType.CONFIG)
    cli_args.parse_args(get_parsed_cli())

    if (cli_args.action is not None) and cli_args.action != ActionType.CONFIG:
        log(log_prefix1 + "ktr-config does not take action arguments.", 2)

    cli_args.action = ActionType.CONFIG

    ktr_bootstrap()

    pkgs = list()

    # if only specified packages are to be processed:
    # process packages only
    if not cli_args.packages_all:
        for name in cli_args.packages:
            pkgs.append(name)

    # if all package are to be processed:
    # get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(
            ktr_get_conf().confdir, "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).rstrip(".conf"))

    # log list of found packages
    log(log_prefix1 + "Packages:", 2)
    for package in pkgs:
        log(log_prefix2 + package, 2)

    # run action for every specified package
    for name in pkgs:
        action = ACTION_DICT[ActionType.CONFIG](
            *get_action_args(cli_args, name, ActionType.CONFIG))
        success = action.execute()

        if success:
            log(log_prefix1 + name + ": Success!")
        else:
            log(log_prefix1 + name + ": Not successful.")

    print()

