"""
kentauros.init.cli
"""

import argparse


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
    help="specify base directory for storing configuration, specs, data")

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
    "----packdir",
    action="store",
    default=None,
    help="specify .src.rpm directory to be used")

# --specdir switch
CLIPARSER.add_argument(
    "--specdir",
    action="store",
    default=None,
    help="specify rpm .spec directory to be used")


# --prefconf switch
CLIPARSER.add_argument(
    "--prefconf",
    action="store",
    default=None,
    help="specify preferred configuration to be used " +\
         "(cli, env, project, user, system, default, fallback)")


CLI_ARGS = CLIPARSER.parse_args()

CLIDEBUG = CLI_ARGS.debug

CLIVERBY = 2 - CLI_ARGS.verby
if CLIVERBY < 0:
    print("DBG: Verbosity levels only range from 0 to 2.")
    CLIVERBY = 0

CLI_BASEDIR = CLI_ARGS.basedir
CLI_CONFDIR = CLI_ARGS.confdir
CLI_DATADIR = CLI_ARGS.datadir
CLI_PACKDIR = CLI_ARGS.packdir
CLI_SPECDIR = CLI_ARGS.specdir

CLI_PREF_CONF = None
if CLI_ARGS.prefconf != None:
    CLI_PREF_CONF = CLI_ARGS.prefconf.upper()

