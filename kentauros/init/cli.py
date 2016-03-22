"""
kentauros.init.cli file
"""

import argparse

from kentauros.definitions import ActionType, KtrConfType, InstanceType


def get_parsed_cli(instance_type=InstanceType.NORMAL):
    """
    # TODO: napoleon docstring
    # TODO: seperate parsing options for ActionTypes (mapping dict?)
    kentauros.init.cli.cli_parse():
    function that builds the kentauros CLI parser and returns the parsed values
    """

    assert isinstance(instance_type, InstanceType)

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

    if instance_type == InstanceType.NORMAL:
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


    elif instance_type == InstanceType.CONFIG:
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


    elif instance_type == InstanceType.CREATE:
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


    cli_args = cliparser.parse_args()

    return cli_args


class CLIArgs:
    """
    # TODO: napoleon docstring
    kentauros.init.cli.CLIArgs:
    class that initialises CLI argument parsing and prepares them for reading
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-statements
    # pylint: disable=too-few-public-methods

    args = None

    def __init__(self, itype=InstanceType.NORMAL):
        # pylint: disable=unsubscriptable-object

        self.instance = itype
        self.debug = False
        self.verby = 2

        self.priconf = None

        self.basedir = "./"
        self.confdir = "./"
        self.datadir = "./"
        self.packdir = "./"
        self.specdir = "./"

        self.action = None
        self.force = False
        self.packages = []
        self.packages_all = False

        if self.instance == InstanceType.CONFIG:
            self.confedit = False
            self.config_section = None
            self.config_key = None
            self.config_value = None

        if self.args is None:
            CLIArgs.args = get_parsed_cli(itype)

        self.debug = self.args.debug

        if (2 - self.args.verby) >= 0:
            self.verby = 2 - self.args.verby
        else:
            self.verby = 0
            print("DEBUG: Verbosity levels only range from 0 to 2.")

        self.basedir = self.args.basedir
        self.confdir = self.args.confdir
        self.datadir = self.args.datadir
        self.packdir = self.args.packdir
        self.specdir = self.args.specdir

        try:
            self.priconf = KtrConfType[self.args.priconf.upper()]
        except AttributeError:
            self.priconf = None
        except KeyError:
            self.priconf = None

        if 'action' in self.args:
            self.action = self.args.action
        elif self.instance == InstanceType.CONFIG:
            self.action = ActionType.CONFIG
        else:
            self.action = None

        if 'package' in self.args:
            self.packages = self.args.package
        else:
            self.packages = list()

        if 'all' in self.args:
            self.packages_all = self.args.all
        else:
            self.packages_all = False

        if 'force' in self.args:
            self.force = self.args.force
        else:
            self.force = False

        if self.instance == InstanceType.CONFIG:
            if ("section" in self.args) and \
               ("key" in self.args) and \
               ("value" in self.args):
                self.confedit = True
                self.config_section = self.args.section
                self.config_key = self.args.key
                self.config_value = self.args.value
            else:
                self.confedit = False

