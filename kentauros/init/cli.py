"""
kentauros.init.cli
"""

import argparse

from kentauros import ActionType


CLIPARSER = argparse.ArgumentParser(
    description="Update, build, upload packages. All from source.",
    prog="kentauros")


# --debug, -d switch
CLIPARSER.add_argument(
    "-d",
    "--debug",
    action="store_const",
    const=True,
    default=False,
    help="enable debug output")

# --verbose, -v, -vv switches
CLIPARSER.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    dest="verby",
    help="enable verbose output. use twice for extra verbosity")

# --basedir switch
CLIPARSER.add_argument(
    "--basedir",
    action="store",
    default=None,
    help="specify base directory for kentauros data")

# --confdir switch
CLIPARSER.add_argument(
    "--confdir",
    action="store",
    default=None,
    help="specify configuration directory to be used")

# --datadir switch
CLIPARSER.add_argument(
    "--datadir",
    action="store",
    default=None,
    help="specify source directory to be used")

# --packdir switch
CLIPARSER.add_argument(
    "--packdir",
    action="store",
    default=None,
    help="specify .src.rpm directory to be used")

# --specdir switch
CLIPARSER.add_argument(
    "--specdir",
    action="store",
    default=None,
    help="specify rpm .spec directory to be used")


# --priconf switch
CLIPARSER.add_argument(
    "--priconf",
    action="store",
    default=None,
    help="specify preferred configuration to be used " +\
         "(cli, env, project, user, system, default, fallback)")


# sub-commands for ktr
PARSERS = CLIPARSER.add_subparsers(
    title="commands",
    description="kentauros accepts the sub-commands given below")


PACKAGEPARSER = argparse.ArgumentParser(add_help=False)
PACKAGEPARSER.add_argument(
    "package",
    action="store",
    nargs="*",
    help="package name")
PACKAGEPARSER.add_argument(
    "-a", "--all",
    action="store_const",
    const=True,
    default=False,
    help="build all packages for which a valid configuration is found")
PACKAGEPARSER.add_argument(
    "-f", "--force",
    action="store_const",
    const=True,
    default=False,
    help="force actions, even if no updates were available")


VERIFYPARSER = PARSERS.add_parser(
    "verify",
    description="verify that package configuration and specification " + \
                "are present and valid",
    help="verify package conf and spec",
    parents=[PACKAGEPARSER])

GETPARSER = PARSERS.add_parser(
    "get",
    description="get sources specified in package configuration",
    help="get package sources",
    parents=[PACKAGEPARSER])

UPDATEPARSER = PARSERS.add_parser(
    "update",
    description="update sources specified in package configuration",
    help="update package sources",
    parents=[PACKAGEPARSER])

CONSTRUCTPARSER = PARSERS.add_parser(
    "construct",
    description="construct source package as specified by package configuration",
    help="construct source package",
    parents=[PACKAGEPARSER])

BUILDPARSER = PARSERS.add_parser(
    "build",
    description="build source package locally as specified by package configuration",
    help="build package locally",
    parents=[PACKAGEPARSER])

UPLOADPARSER = PARSERS.add_parser(
    "upload",
    description="upload source package to cloud build service or similar",
    help="upload source package",
    parents=[PACKAGEPARSER])

CONFIGPARSER = PARSERS.add_parser(
    "config",
    description="change package configuration stored in package.conf file",
    help="change configuration values",
    parents=[PACKAGEPARSER])
CONFIGPARSER.add_argument(
    "-s", "--section",
    action="store",
    help="specify section of config file")
CONFIGPARSER.add_argument(
    "-k", "--key",
    action="store",
    help="specify key of config file in section specified by --section")
CONFIGPARSER.add_argument(
    "-V", "--value",
    action="store",
    help="specify value to be written to --section/--key")

CREATEPARSER = PARSERS.add_parser(
    "create",
    description="create new package and provide templates for conf and spec",
    help="create package from template",
    parents=[PACKAGEPARSER])


VERIFYPARSER.set_defaults(action=ActionType.VERIFY)
GETPARSER.set_defaults(action=ActionType.GET)
UPDATEPARSER.set_defaults(action=ActionType.UPDATE)
CONSTRUCTPARSER.set_defaults(action=ActionType.CONSTRUCT)
BUILDPARSER.set_defaults(action=ActionType.BUILD)
UPLOADPARSER.set_defaults(action=ActionType.UPLOAD)
CONFIGPARSER.set_defaults(action=ActionType.CONFIG)
CREATEPARSER.set_defaults(action=ActionType.CREATE)


CLI_ARGS = CLIPARSER.parse_args()

CLIDEBUG = CLI_ARGS.debug

CLIVERBY = 2 - CLI_ARGS.verby
if CLIVERBY < 0:
    print("DEBUG: Verbosity levels only range from 0 to 2.")
    CLIVERBY = 0

CLI_BASEDIR = CLI_ARGS.basedir
CLI_CONFDIR = CLI_ARGS.confdir
CLI_DATADIR = CLI_ARGS.datadir
CLI_PACKDIR = CLI_ARGS.packdir
CLI_SPECDIR = CLI_ARGS.specdir

CLI_PREF_CONF = None
if CLI_ARGS.priconf != None:
    CLI_PREF_CONF = CLI_ARGS.priconf.upper()

if "action" in CLI_ARGS:
    CLI_ACTION = CLI_ARGS.action
else:
    CLI_ACTION = None

CLI_PACKAGES = CLI_ARGS.package
CLI_PACKAGES_ALL = CLI_ARGS.all
CLI_FORCE = CLI_ARGS.force

CLI_CONFIG_SECTION = CLI_ARGS.section
CLI_CONFIG_KEY = CLI_ARGS.key
CLI_CONFIG_VALUE = CLI_ARGS.value

