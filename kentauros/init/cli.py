"""
This module contains functions for constructing an `argparse` command line
argument parser, and parsing the determined command line arguments. It also
contains classes which provide methods that return parsed CLI arguments,
depending on where the `kentauros` module is used from.
"""


import argparse

from kentauros.definitions import ActionType, KtrConfType, InstanceType


def get_cli_parser_base():
    """
    This function constructs and returns a basic parser for command line
    arguments, which will be further processed and added to by other functions.

    The arguments parsed by this basic parser include:

    * ``--debug`` (``-d``) switch to enable debug messages in kentauros and for
      subprocesses
    * ``--verbose`` (``-v``, ``-vv``) switch to control how many informational
      messages will be printed (twice for extra verbosity)
    * ``--basedir=BASEDIR`` argument to set base directory for kentauros files
      (optional)
    * ``--confdir=CONFDIR`` argument for directly specifying the directory which
      contains package configuration files (optional)
    * ``--datadir=DATADIR`` argument for directly specifying the directory which
      contains package sources (optional)
    * ``--packdir=PACKDIR`` argument for directly specifying the directory which
      contains constructed buildable pre-packages (optional)
    * ``--specdir=SPECDIR`` argument for directly specifying the directory which
      contains instructions for building binaries from source (optional)

    Returns:
        argparse.ArgumentParser: basic CLI argument parser
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


def get_cli_parser_normal(cliparser: argparse.ArgumentParser):
    """
    This function constructs and returns a parser for command line arguments,
    which is used for "normal" execution (e.g. invoking the ``ktr`` script).

    The arguments parsed by this parser include those from the basic parser,
    and, additionally:

    * package name(s) to specify which packages to process explicitly
    * ``--all`` (``-a``) switch to enable processing all packages in ``CONFDIR``
    * ``--force`` (``-f``) switch to force actions which would not be executed

    Arguments:
        argparse.ArgumentParser cliparser: basic argument parser got from
                                           :py:func:`get_cli_parser_base()`

    Returns:
        argparse.ArgumentParser: CLI argument parser for ``ktr`` script
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


def get_cli_parser_config(cliparser: argparse.ArgumentParser):
    """
    This function constructs and returns a parser for command line arguments,
    which is used when changing package settings (e.g. by invoking the
    ``ktr-config`` script).

    The arguments parsed by this parser include those from the basic parser,
    and, additionally:

    * package name(s) to specify which packages to process explicitly
    * ``--all`` (``-a``) switch to enable processing all packages in ``CONFDIR``
    * ``--section`` (``-s``) argument to specify section of config file
    * ``--key`` (``-k``) argument to specify key in section of config file
    * ``--value`` (``-V``) argument to specify the value to be written

    Arguments:
        argparse.ArgumentParser cliparser: basic argument parser got from
                                           :py:func:`get_cli_parser_base()`

    Returns:
        argparse.ArgumentParser: CLI argument parser for ``ktr-config`` script
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


def get_cli_parser_create(cliparser: argparse.ArgumentParser):
    """
    This function constructs and returns a parser for command line arguments,
    which is used when creating a new package from template (not used yet).

    The arguments parsed by this parser include those from the basic parser,
    and, additionally:

    * package name(s) to specify which packages to create
    * ``--force`` (``-f``) switch to force action

    Arguments:
        argparse.ArgumentParser cliparser: basic argument parser got from
                                           :py:func:`get_cli_parser_base()`

    Returns:
        argparse.ArgumentParser: CLI argument parser for ``ktr-create`` script
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


def get_cli_parser(instance_type: InstanceType=InstanceType.NORMAL):
    """
    This function returns a parser for command line arguments with certain
    switches and arguments, depending on which kentauros instance it is used
    for.

    Arguments:
        InstanceType instance_type: invocation type (which script) - this
                                    determines which CLI switches and arguments
                                    will be available and defaults to normal
                                    invocation

    Returns:
        argparse.ArgumentParser: CLI argument parser for the specified instance
    """

    assert isinstance(instance_type, InstanceType)

    parser_dict = dict()
    parser_dict[InstanceType.NORMAL] = get_cli_parser_normal
    parser_dict[InstanceType.CONFIG] = get_cli_parser_config
    parser_dict[InstanceType.CREATE] = get_cli_parser_create

    cliparser = parser_dict[instance_type](get_cli_parser_base())

    return cliparser


def get_parsed_cli(instance_type: InstanceType=InstanceType.NORMAL):
    """
    This function returns a `Namespace` object which contains the parsed CLI
    switches and arguments, as specified in the
    :py:class:`argparse.ArgumentParser` constructing functions in this module -
    and also depending on the instance type specified.

    Arguments:
        InstanceType instance_type: invocation type (which script) - this
                                    determines which CLI switches and arguments
                                    will be available and defaults to normal
                                    invocation

    Returns:
        Namespace: parsed CLI arguments and switches
    """

    cli_args = get_cli_parser(instance_type).parse_args()

    return cli_args


class CLIArgs:
    """
    This class represents the parsed command line arguments and switches used
    with a kentauros script. It stores the parsed CLI arguments between class
    instantiations (in a class variable), so the CLI will be parsed only once.
    It also provides simple method calls for getting settings from the parsed
    CLI.

    Attributes:
        args: permanent (instance-independent) storage of parsed CLI arguments
              (``None`` at first and set later - at first initialisation)

    Arguments:
        InstanceType itype: type of CLI to be created, parsed and stored
    """

    args = None

    def __init__(self, itype: InstanceType=InstanceType.NORMAL):
        if self.args is None:
            CLIArgs.args = get_parsed_cli(itype)

    def get_debug(self):
        """
        This method simply returns whether the ``--debug`` or ``-d`` switch has
        been set at the command line.

        Returns:
            bool: debug *on* or *off*
        """

        return self.args.debug

    def get_verby(self):
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

    def get_priconf(self):
        """
        This method returns the preferred configuration file location (as an
        instance of :py:class:`KtrConfType`).

        Returns:
            KtrConfType: type of the preferred configuration
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
        This method returns kentauros BASEDIR specified by CLI argument.

        Returns:
            str:  specified BASEDIR

        Returns:
            None: no BASEDIR specified
        """

        return self.args.basedir

    def get_ktr_confdir(self):
        """
        This method returns kentauros CONFDIR specified by CLI argument.

        Returns:
            str:  specified CONFDIR

        Returns:
            None: no CONFDIR specified
        """

        return self.args.confdir

    def get_ktr_datadir(self):
        """
        This method returns kentauros DATADIR specified by CLI argument.

        Returns:
            str:  specified DATADIR

        Returns:
            None: no DATADIR specified
        """

        return self.args.datadir

    def get_ktr_packdir(self):
        """
        This method returns kentauros PACKDIR specified by CLI argument.

        Returns:
            str:  specified PACKDIR

        Returns:
            None: no PACKDIR specified
        """

        return self.args.packdir

    def get_ktr_specdir(self):
        """
        This method returns kentauros SPECDIR specified by CLI argument.

        Returns:
            str:  specified SPECDIR

        Returns:
            None: no SPECDIR specified
        """

        return self.args.specdir

    def get_action(self):
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

    def get_packages(self):
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

    def get_packages_all(self):
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

    def get_force(self):
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


class CLIArgsConfig(CLIArgs):
    """
    This class represents the parsed command line arguments and switches used
    with a kentauros script (in this case: the ``ktr-config`` script). It stores
    the parsed CLI arguments between class instantiations (in a class variable),
    so the CLI will be parsed only once. It also provides simple method calls
    for getting settings from the parsed CLI.

    Attributes:
        args: permanent (instance-independent) storage of parsed CLI arguments
              (``None`` at first and set later - at first initialisation)
    """

    def __init__(self):
        super().__init__()

        if self.args is None:
            CLIArgs.args = get_parsed_cli(InstanceType.CONFIG)

    def get_config_section(self):
        """
        This method returns the configuration file section as specified by
        CLI argument.

        Returns:
            str:  specified section
        """

        return self.args.section

    def get_config_key(self):
        """
        This method returns the configuration file key as specified by CLI
        argument.

        Returns:
            str:  specified key
        """

        return self.args.key

    def get_config_value(self):
        """
        This method returns the configuration file value as specified by CLI
        argument.

        Returns:
            str:  specified value
        """

        return self.args.value

    def get_confedit(self):
        """
        This method returns whether everything necessary for editing a config
        file has been supplied at CLI (section, key, value).

        Returns:
            bool: ``True`` if everything was specified, ``False`` if not
        """

        return ("section" in self.args) and \
               ("key" in self.args) and \
               ("value" in self.args)


CLI_ARGS_DICT = dict()
""" This dictionary contains a mapping from :py:class:`InstanceType` members to
their respective :py:class:`CLIArgs` class or subclass constructors.
"""

CLI_ARGS_DICT[InstanceType.NORMAL] = CLIArgs
CLI_ARGS_DICT[InstanceType.CREATE] = CLIArgs
CLI_ARGS_DICT[InstanceType.CONFIG] = CLIArgsConfig

