"""
kentauros.init.cli
"""

import argparse

from kentauros.definitions import ActionType


def cli_parse():
    """
    kentauros.init.cli.cli_parse():
    function that builds the kentauros CLI parser and returns the parsed values
    """
    cliparser = argparse.ArgumentParser(
        description="Update, build, upload packages. All from source.",
        prog="kentauros")

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
        description="build source package locally as specified by package configuration",
        help="build package locally",
        parents=[package_parser])

    chain_parser = parsers.add_parser(
        "chain",
        description="run chain reaction (get, update, construct, build, upload)",
        help="comlete source to upload toolchain",
        parents=[package_parser])

    config_parser = parsers.add_parser(
        "config",
        description="change package configuration stored in package.conf file",
        help="change configuration values",
        parents=[package_parser])
    config_parser.add_argument(
        "-s", "--section",
        action="store",
        default=None,
        help="specify section of config file")
    config_parser.add_argument(
        "-k", "--key",
        action="store",
        default=None,
        help="specify key of config file in section specified by --section")
    config_parser.add_argument(
        "-V", "--value",
        action="store",
        default=None,
        help="specify value to be written to --section/--key")

    construct_parser = parsers.add_parser(
        "construct",
        description="construct source package as specified by package configuration",
        help="construct source package",
        parents=[package_parser])

    create_parser = parsers.add_parser(
        "create",
        description="create new package and provide templates for conf and spec",
        help="create package from template",
        parents=[package_parser])

    export_parser = parsers.add_parser(
        "export",
        description="export sources from repository to tarball",
        help="export package sources",
        parents=[package_parser])

    get_parser = parsers.add_parser(
        "get",
        description="get sources specified in package configuration",
        help="get package sources",
        parents=[package_parser])

    status_parser = parsers.add_parser(
        "status",
        description="display kentauros status (configuration, packages)",
        help="display kentauros status",
        parents=[package_parser])

    update_parser = parsers.add_parser(
        "update",
        description="update sources specified in package configuration",
        help="update package sources",
        parents=[package_parser])

    upload_parser = parsers.add_parser(
        "upload",
        description="upload source package to cloud build service or similar",
        help="upload source package",
        parents=[package_parser])

    verify_parser = parsers.add_parser(
        "verify",
        description="verify that package configuration and specification " + \
                    "are present and valid",
        help="verify package conf and spec",
        parents=[package_parser])

    build_parser.set_defaults(action=ActionType.BUILD)
    chain_parser.set_defaults(action=ActionType.CHAIN)
    config_parser.set_defaults(action=ActionType.CONFIG)
    construct_parser.set_defaults(action=ActionType.CONSTRUCT)
    create_parser.set_defaults(action=ActionType.CREATE)
    export_parser.set_defaults(action=ActionType.EXPORT)
    get_parser.set_defaults(action=ActionType.GET)
    status_parser.set_defaults(action=ActionType.STATUS, all=True)
    update_parser.set_defaults(action=ActionType.UPDATE)
    upload_parser.set_defaults(action=ActionType.UPLOAD)
    verify_parser.set_defaults(action=ActionType.VERIFY)

    cli_args = cliparser.parse_args()

    return cli_args


class CLIArgs(dict):
    """
    kentauros.init.cli.CLIArgs:
    class that initialises CLI argument parsing and prepares them for reading
    """
    def __init__(self, cli_args):
        super().__init__()
        # set values according to CLI arguments
        self['debug'] = cli_args.debug

        if (2 - cli_args.verby) >= 0:
            self['verby'] = 2 - cli_args.verby
        else:
            self['verby'] = 0
            print("DEBUG: Verbosity levels only range from 0 to 2.")

        self.basedir = cli_args.basedir
        self.confdir = cli_args.confdir
        self.datadir = cli_args.datadir
        self.packdir = cli_args.packdir
        self.specdir = cli_args.specdir

        self['priconf'] = cli_args.priconf

        if 'action' in cli_args:
            self['action'] = cli_args.action
        else:
            self['action'] = None

        if 'package' in cli_args:
            self['packages'] = cli_args.package
        else:
            self['packages'] = list()

        if 'all' in cli_args:
            self['packages_all'] = cli_args.all
        else:
            self['packages_all'] = False

        if 'force' in cli_args:
            self['force'] = cli_args.force
        else:
            self['force'] = False

        if ("section" in cli_args) and \
           ("key" in cli_args) and \
           ("value" in cli_args):
            self['confedit'] = True
            self['config_section'] = cli_args.section
            self['config_key'] = cli_args.key
            self['config_value'] = cli_args.value
        else:
            self['confedit'] = False


CLI_ARGS = CLIArgs(cli_parse())

