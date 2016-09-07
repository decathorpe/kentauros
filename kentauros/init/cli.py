"""
This module contains functions for constructing an `argparse` command line
argument parser, and parsing the determined command line arguments. It also
contains classes which provide methods that return parsed CLI arguments,
depending on where the `kentauros` module is used from.
"""


from argparse import ArgumentParser

from kentauros.definitions import ActionType, KtrConfType


def get_cli_parser_base() -> ArgumentParser:
    """
    This function constructs and returns a basic parser for command line arguments, which will be
    further processed and added to by other functions.

    The arguments parsed by this basic parser include:

    * ``--debug`` (``-d``) switch to enable debug messages in kentauros and for subprocesses
    * ``--verbose`` (``-v``, ``-vv``) switch to control how many informational messages will be
      printed (twice for extra verbosity)
    * ``--basedir=BASEDIR`` argument to set base directory for kentauros files (optional)

    Returns:
        ArgumentParser: basic CLI argument parser
    """

    cliparser = ArgumentParser(
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

    return cliparser


def get_cli_parser_normal(cliparser: ArgumentParser) -> ArgumentParser:
    """
    This function constructs and returns a parser for command line arguments,
    which is used for "normal" execution (e.g. invoking the ``ktr`` script).

    The arguments parsed by this parser include those from the basic parser,
    and, additionally:

    * package name(s) to specify which packages to process explicitly
    * ``--all`` (``-a``) switch to enable processing all packages in ``CONFDIR``
    * ``--force`` (``-f``) switch to force actions which would not be executed

    Arguments:
        ArgumentParser cliparser: basic argument parser got from
                                  :py:func:`get_cli_parser_base()`

    Returns:
        ArgumentParser: CLI argument parser for ``ktr`` script
    """

    assert isinstance(cliparser, ArgumentParser)

    # sub-commands for ktr
    parsers = cliparser.add_subparsers(
        title="commands",
        description="kentauros accepts the sub-commands given below")

    package_parser = ArgumentParser(add_help=False)
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
        description="verify that package *.conf and spec are present and valid",
        help="verify package conf and spec",
        parents=[package_parser])
    verify_parser.set_defaults(action=ActionType.VERIFY)

    return cliparser


def get_cli_parser() -> ArgumentParser:
    """
    This function returns a parser for command line arguments with certain
    switches and arguments, depending on which kentauros instance it is used
    for.

    Arguments:
        InstanceType itype: invocation type (which script) - this determines
                            which CLI switches and arguments will be available
                            and defaults to normal invocation

    Returns:
        ArgumentParser: CLI argument parser for the specified instance
    """

    return get_cli_parser_normal(get_cli_parser_base())


def get_parsed_cli() -> ArgumentParser:
    """
    This function returns a `Namespace` object which contains the parsed CLI
    switches and arguments, as specified in the
    :py:class:`ArgumentParser` constructing functions in this module -
    and also depending on the instance type specified.

    Arguments:
        InstanceType itype: invocation type (which script) - this determines
                            which CLI switches and arguments will be available
                            and defaults to normal invocation

    Returns:
        Namespace: parsed CLI arguments and switches
    """

    cli_args = get_cli_parser().parse_args()

    return cli_args


class CLIArgs:
    """
    This class represents the parsed command line arguments and switches used
    with a kentauros script. It stores the parsed CLI arguments between class
    instantiations (in a class variable), so the CLI will be parsed only once.
    It also provides simple method calls for getting settings from the parsed
    CLI.

    Arguments:
        InstanceType itype: type of CLI to be created, parsed and stored
    """

    args = None
    """ArgumentParser: This class variable contains the permanent (instance-
    independent) storage of parsed CLI arguments. It is initially set to `None`
    and generated at the time of the first class initialisation.
    """

    def __init__(self):
        if self.args is None:
            CLIArgs.args = get_parsed_cli()

    def get_debug(self) -> bool:
        """
        This method simply returns whether the ``--debug`` or ``-d`` switch has
        been set at the command line.

        Returns:
            bool: debug *on* or *off*
        """

        return self.args.debug

    def get_verby(self) -> int:
        """
        This method returns how often the ``--verbose`` or ``-v`` switch has
        been set at the command line, subtracted from 2. This results in a
        lowest verbosity level of *2* (comparable to ``--quiet``), a medium
        verbosity level of *1* (normal verbosity) and a high verbosity level of
        *0* (very verbose).

        Returns:
            int: verbosity level (0 to 2)
        """

        if (2 - self.args.verby) >= 0:
            return 2 - self.args.verby
        else:
            print("DEBUG: Verbosity levels only range from 0 to 2.")
            return 0

    def get_priconf(self) -> KtrConfType:
        """
        This method returns the preferred configuration file location (as an
        instance of :py:class:`KtrConfType`).

        Returns:
            KtrConfType: type of the preferred configuration
        """

        try:
            return KtrConfType[self.args.priconf.upper()]
        except AttributeError:
            return None
        except KeyError:
            return None

    def get_ktr_basedir(self) -> str:
        """
        This method returns kentauros BASEDIR specified by CLI argument.

        Returns:
            str:  specified BASEDIR

        Returns:
            None: no BASEDIR specified
        """

        return self.args.basedir

    def get_action(self) -> ActionType:
        """
        This method returns which package action has been specified at CLI.
        If this is ``None``, something went wrong and no action type will be
        returned.

        Returns:
            ActionType: type of action that will be executed
        """

        if 'action' in self.args:
            return self.args.action
        return ActionType.NONE

    def get_packages(self) -> list:
        """
        This method returns all the package names which were collected from
        the CLI arguments.

        Returns:
            list: specified packages in a list
        """

        if 'package' in self.args:
            return self.args.package
        else:
            return list()

    def get_packages_all(self) -> bool:
        """
        This method simply returns whether the ``--all`` or ``-a`` switch has
        been set at the command line.

        Returns:
            bool: parse all packages *on* or *off*
        """

        if 'all' in self.args:
            return self.args.all
        else:
            return False

    def get_force(self) -> bool:
        """
        This method simply returns whether the ``--force`` or ``-f`` switch has
        been set at the command line.

        Returns:
            bool: force package actions *on* or *off*
        """

        if 'force' in self.args:
            return self.args.force
        else:
            return False
