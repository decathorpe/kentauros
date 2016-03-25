"""
This module contains functions for constructing an `argparse` command line
argument parser, and parsing the determined command line arguments.
"""

import argparse

from kentauros.definitions import ActionType, KtrConfType, InstanceType


def get_cli_parser_base():
    """
    # TODO: napoleon docstring
    """

    cliparser = argparse.ArgumentParser(
        description="execute actions on packages and their sources",
        prog="ktr")

    # --debug, -d switch
    cliparser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=True,
        default=False,
        help="enable debug output")

    # --verbose, -v, -vv switches
    cliparser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verby",
        help="enable verbose output. use twice for extra verbosity")

    # --basedir switch
    cliparser.add_argument(
        "--basedir",
        action="store",
        default=None,
        help="specify base directory for kentauros data")

    # --confdir switch
    cliparser.add_argument(
        "--confdir",
        action="store",
        default=None,
        help="specify configuration directory to be used")

    # --datadir switch
    cliparser.add_argument(
        "--datadir",
        action="store",
        default=None,
        help="specify source directory to be used")

    # --packdir switch
    cliparser.add_argument(
        "--packdir",
        action="store",
        default=None,
        help="specify .src.rpm directory to be used")

    # --specdir switch
    cliparser.add_argument(
        "--specdir",
        action="store",
        default=None,
        help="specify rpm .spec directory to be used")

    # --priconf switch
    cliparser.add_argument(
        "--priconf",
        action="store",
        default=None,
        help="specify preferred configuration to be used " +\
             "(cli, env, project, user, system, default, fallback)")

    return cliparser


def get_cli_parser_normal(cliparser):
    """
    # TODO: napoleon docstring
    """

    assert isinstance(cliparser, argparse.ArgumentParser)

    # sub-commands for ktr
    parsers = cliparser.add_subparsers(
        title="commands",
        description="kentauros accepts the sub-commands given below")

    package_parser = argparse.ArgumentParser(add_help=False)
    package_parser.add_argument(
        "package",
        action="store",
        nargs="*",
        help="package name")
    package_parser.add_argument(
        "-a", "--all",
        action="store_const",
        const=True,
        default=False,
        help="apply action to every package with valid configuration")
    package_parser.add_argument(
        "-f", "--force",
        action="store_const",
        const=True,
        default=False,
        help="force actions, even if no updates were available")

    build_parser = parsers.add_parser(
        "build",
        description="build package locally as specified by package.conf",
        help="build package locally",
        parents=[package_parser])
    build_parser.set_defaults(action=ActionType.BUILD)

    chain_parser = parsers.add_parser(
        "chain",
        description="run toolchain (get/update, construct, build, upload)",
        help="comlete source to upload toolchain",
        parents=[package_parser])
    chain_parser.set_defaults(action=ActionType.CHAIN)

    clean_parser = parsers.add_parser(
        "clean",
        description="clean sources of specified package(s)",
        help="clean package sources",
        parents=[package_parser])
    clean_parser.set_defaults(action=ActionType.CLEAN)

    construct_parser = parsers.add_parser(
        "construct",
        description="construct source package as specified by *.conf",
        help="construct source package",
        parents=[package_parser])
    construct_parser.set_defaults(action=ActionType.CONSTRUCT)

    export_parser = parsers.add_parser(
        "export",
        description="export sources from repository to tarball",
        help="export package sources",
        parents=[package_parser])
    export_parser.set_defaults(action=ActionType.EXPORT)

    get_parser = parsers.add_parser(
        "get",
        description="get sources specified in package configuration",
        help="get package sources",
        parents=[package_parser])
    get_parser.set_defaults(action=ActionType.GET)

    prepare_parser = parsers.add_parser(
        "prepare",
        description="prepare sources for further use (get/update, export)",
        help="prepare source tarball for package",
        parents=[package_parser])
    prepare_parser.set_defaults(action=ActionType.PREPARE)

    refresh_parser = parsers.add_parser(
        "refresh",
        description="refresh package sources (clean, get)",
        help="refresh package sources",
        parents=[package_parser])
    refresh_parser.set_defaults(action=ActionType.REFRESH)

    status_parser = parsers.add_parser(
        "status",
        description="display kentauros status (configuration, packages)",
        help="display kentauros status",
        parents=[package_parser])
    status_parser.set_defaults(action=ActionType.STATUS)

    update_parser = parsers.add_parser(
        "update",
        description="update sources specified in package configuration",
        help="update package sources",
        parents=[package_parser])
    update_parser.set_defaults(action=ActionType.UPDATE)

    upload_parser = parsers.add_parser(
        "upload",
        description="upload source package to cloud service or similar",
        help="upload source package",
        parents=[package_parser])
    upload_parser.set_defaults(action=ActionType.UPLOAD)

    verify_parser = parsers.add_parser(
        "verify",
        description="verify that package *.conf and spec " + \
                    "are present and valid",
        help="verify package conf and spec",
        parents=[package_parser])
    verify_parser.set_defaults(action=ActionType.VERIFY)

    return cliparser


def get_cli_parser_config(cliparser):
    """
    # TODO: napoleon docstring
    """

    assert isinstance(cliparser, argparse.ArgumentParser)

    cliparser.add_argument(
        "package",
        action="store",
        nargs="*",
        help="package name")
    cliparser.add_argument(
        "-a", "--all",
        action="store_const",
        const=True,
        default=False,
        help="apply action to every package with valid configuration")

    cliparser.add_argument(
        "-s", "--section",
        action="store",
        default=None,
        help="specify section of config file")
    cliparser.add_argument(
        "-k", "--key",
        action="store",
        default=None,
        help="specify key of config file in section specified by --section")
    cliparser.add_argument(
        "-V", "--value",
        action="store",
        default=None,
        help="specify value to be written to --section/--key")
    cliparser.set_defaults(action=ActionType.CONFIG)

    return cliparser


def get_cli_parser_create(cliparser):
    """
    # TODO: napoleon docstring
    """

    assert isinstance(cliparser, argparse.ArgumentParser)

    cliparser.add_argument(
        "package",
        action="store",
        nargs="*",
        help="package name")
    cliparser.set_defaults(action=ActionType.CREATE)
    cliparser.add_argument(
        "-f", "--force",
        action="store_const",
        const=True,
        default=False,
        help="force actions, even if no updates were available")

    return cliparser


def get_cli_parser(instance_type=InstanceType.NORMAL):
    """
    # TODO: napoleon docstring
    """

    assert isinstance(instance_type, InstanceType)

    parser_dict = dict()
    parser_dict[InstanceType.NORMAL] = get_cli_parser_normal
    parser_dict[InstanceType.CONFIG] = get_cli_parser_config
    parser_dict[InstanceType.CREATE] = get_cli_parser_create

    cliparser = parser_dict[instance_type](get_cli_parser_base())

    return cliparser


def get_parsed_cli(instance_type=InstanceType.NORMAL):
    """
    # TODO: napoleon docstring
    """

    cli_args = get_cli_parser(instance_type).parse_args()

    return cli_args


class CLIArgs:
    """
    # TODO: napoleon docstring
    kentauros.init.cli.CLIArgs:
    class that initialises CLI argument parsing and prepares them for reading
    """

    args = None

    def __init__(self, itype=InstanceType.NORMAL):
        if self.args is None:
            CLIArgs.args = get_parsed_cli(itype)

    def get_debug(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.debug

    def get_verby(self):
        """
        # TODO: napoleon docstring
        """

        if (2 - self.args.verby) >= 0:
            return 2 - self.args.verby
        else:
            print("DEBUG: Verbosity levels only range from 0 to 2.")
            return 0

    def get_priconf(self):
        """
        # TODO: napoleon docstring
        """

        # pylint: disable=unsubscriptable-object

        try:
            return KtrConfType[self.args.priconf.upper()]
        except AttributeError:
            return None
        except KeyError:
            return None

    def get_ktr_basedir(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.basedir

    def get_ktr_confdir(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.confdir

    def get_ktr_datadir(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.datadir

    def get_ktr_packdir(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.packdir

    def get_ktr_specdir(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.specdir

    def get_action(self):
        """
        # TODO: napoleon docstring
        """

        if 'action' in self.args:
            return self.args.action
        return ActionType.NONE

    def get_packages(self):
        """
        # TODO: napoleon docstring
        """

        if 'package' in self.args:
            return self.args.package
        else:
            return list()

    def get_packages_all(self):
        """
        # TODO: napoleon docstring
        """

        if 'all' in self.args:
            return self.args.all
        else:
            return False

    def get_force(self):
        """
        # TODO: napoleon docstring
        """

        if 'force' in self.args:
            return self.args.force
        else:
            return False


class CLIArgsConfig(CLIArgs):
    """
    # TODO: napoleon docstring
    """

    def __init__(self):
        super().__init__()

        if self.args is None:
            CLIArgs.args = get_parsed_cli(InstanceType.CONFIG)

    def get_config_section(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.section

    def get_config_key(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.key

    def get_config_value(self):
        """
        # TODO: napoleon docstring
        """

        return self.args.value

    def get_confedit(self):
        """
        # TODO: napoleon docstring
        """

        return ("section" in self.args) and \
               ("key" in self.args) and \
               ("value" in self.args)


CLI_ARGS_DICT = dict()
CLI_ARGS_DICT[InstanceType.NORMAL] = CLIArgs
CLI_ARGS_DICT[InstanceType.CREATE] = CLIArgs
CLI_ARGS_DICT[InstanceType.CONFIG] = CLIArgsConfig

