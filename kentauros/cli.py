"""
kentauros.cli
"""

import argparse


def get_pkglist(args):
    """
    kentauros.cli.get_pkglist()
    reads command line package arguments, reads lines from pkglist files,
    and returns a list of all gathered packages.
    """
    packages = list()

    for pkg in args.package:
        packages.append(pkg)

    if args.pkgfile != None:
        for pkgfile in args.pkgfile:
            for line in pkgfile:
                packages.append(line.rstrip("\n\r"))

    return packages


CLIPARSER = argparse.ArgumentParser(
    description="Update, build, upload packages. All from source.",
    prog="kentauros")
CLIPARSER.add_argument(
    "-d",
    "--debug",
    action="store_const",
    const=True,
    default=False,
    help="enable debug output")
CLIPARSER.add_argument(
    "-v",
    "--verbose",
    action="store_const",
    const=True,
    default=False,
    help="enable verbose output")


PACKAGEPARSER = argparse.ArgumentParser(add_help=False)
PACKAGEPARSER.add_argument(
    "package",
    action="store",
    nargs="*",
    type=str,
    help="package name")
PACKAGEPARSER.add_argument(
    "--pkgfile",
    action="store",
    nargs="*",
    type=argparse.FileType("r"),
    help="pkgfile (containing one package name per line)")


PARSERS = CLIPARSER.add_subparsers(
    title="commands",
    description="kentauros accepts the sub-commands given below",
    help="get sub-command-specific help")


CREATEPARSER = PARSERS.add_parser(
    "create",
    description="create skeleton file structure for packages",
    help="create package directory and configuration files",
    parents=[PACKAGEPARSER])


VERIFYPARSER = PARSERS.add_parser(
    "verify",
    description="verify that package directory, configuration and package " +
        "specification are present and valid",
    help="verify package files and configuration",
    parents=[PACKAGEPARSER])


UPDATEPARSER = PARSERS.add_parser(
    "update",
    description="update specified source repository (bzr, git)",
    help="update specified source repository (bzr, git)",
    parents=[PACKAGEPARSER])
UPDATEPARSER.add_argument(
    "-r",
    "--refresh",
    action="store_const",
    const=True,
    default=False,
    help="force re-downloading sources")


BUILDPARSER = PARSERS.add_parser(
    "build",
    description="build updated source packages (e.g. srpms)",
    help="build updated source packages (e.g. srpms)",
    parents=[PACKAGEPARSER])
BUILDPARSER.add_argument(
    "-f",
    "--force",
    action="store_const",
    const=True,
    default=False,
    help="force building source packages, even if sources were not updated " +
    "(e.g. after changing packaging related files)")


UPLOADPARSER = PARSERS.add_parser(
    "upload",
    description="upload built source packages (e.g. to copr)",
    help="upload built source packages (e.g. to copr)",
    parents=[PACKAGEPARSER])
UPLOADPARSER.add_argument(
    "-w",
    "--watch",
    action="store_const",
    const=True,
    default=False,
    help="watch online build service package builder status")
UPLOADPARSER.add_argument(
    "-f",
    "--force",
    action="store_const",
    const=True,
    default=False,
    help="force uploading packages, even if sources were not updated " +
    "(e.g. after changing packaging related files)")

CREATEPARSER.set_defaults(action="create")
VERIFYPARSER.set_defaults(action="verify")
UPDATEPARSER.set_defaults(action="update")
BUILDPARSER.set_defaults(action="build")
UPLOADPARSER.set_defaults(action="upload")

CLI_ARGS = CLIPARSER.parse_args()
DEBUG = CLI_ARGS.debug or CLI_ARGS.verbose
PACKAGES = get_pkglist(CLI_ARGS)

