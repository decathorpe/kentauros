import configparser
import glob
import os

from argparse import ArgumentParser, _SubParsersAction


# pylint: disable=unused-argument
# noinspection PyUnusedLocal
def package_name_completer(prefix, **kwargs):
    if os.path.exists("kentaurosrc"):
        config = configparser.ConfigParser()
        config.read("kentaurosrc")

        try:
            basedir = os.path.abspath(config.get("main", "basedir"))
        except configparser.NoSectionError:
            basedir = os.path.abspath(os.getcwd())
        except configparser.NoOptionError:
            basedir = os.path.abspath(os.getcwd())
    else:
        basedir = os.path.abspath(os.getcwd())

    paths = os.path.join(basedir, "configs", "*.conf")

    files = glob.glob(paths)

    return (os.path.basename(v).replace(".conf", "")
            for v in files
            if os.path.basename(v).replace(".conf", "").startswith(prefix))


def add_source_parser(parsers: _SubParsersAction,
                      package_parser: ArgumentParser) -> ArgumentParser:

    source_parser: ArgumentParser = parsers.add_parser(
        "source",
        aliases=["s", "so", "sou", "sour", "sourc", "src"],
        description="interact with the package's sources",
        help="interact with sources")
    source_parser.set_defaults(module="source")

    source_parsers: _SubParsersAction = source_parser.add_subparsers()

    clean_parser: ArgumentParser = source_parsers.add_parser(
        "clean",
        aliases=["c", "cl", "cle", "clea"],
        description="clean up sources",
        help="clean up sources",
        parents=[package_parser])
    clean_parser.set_defaults(module_action="clean")

    export_parser: ArgumentParser = source_parsers.add_parser(
        "export",
        aliases=["e", "ex", "exp", "expo", "expor"],
        description="export sources",
        help="export sources",
        parents=[package_parser])
    export_parser.set_defaults(module_action="export")

    get_parser: ArgumentParser = source_parsers.add_parser(
        "get",
        aliases=["g", "ge"],
        description="get sources",
        help="get sources",
        parents=[package_parser])
    get_parser.set_defaults(module_action="get")

    prepare_parser: ArgumentParser = source_parsers.add_parser(
        "prepare",
        aliases=["p", "pr", "pre", "prep", "prepa", "prepar"],
        description="prepare sources",
        help="prepare sources",
        parents=[package_parser])
    prepare_parser.set_defaults(module_action="prepare")

    refresh_parser: ArgumentParser = source_parsers.add_parser(
        "refresh",
        aliases=["r", "re", "ref", "refr", "refre", "refres"],
        description="refresh sources",
        help="refresh sources",
        parents=[package_parser])
    refresh_parser.set_defaults(module_action="refresh")

    status_parser: ArgumentParser = source_parsers.add_parser(
        "status",
        aliases=["s", "st", "sta", "stat", "statu"],
        description="print source status",
        help="print source status",
        parents=[package_parser])
    status_parser.set_defaults(module_action="status")

    update_parser: ArgumentParser = source_parsers.add_parser(
        "update",
        aliases=["u", "up", "upd", "upda", "updat"],
        description="update sources",
        help="update sources",
        parents=[package_parser])
    update_parser.set_defaults(module_action="update")

    verify_parser: ArgumentParser = source_parsers.add_parser(
        "verify",
        aliases=["v", "ve", "ver", "veri", "verif"],
        description="verify sources functionality",
        help="verify sources functionality",
        parents=[package_parser])
    verify_parser.set_defaults(module_action="verify")

    return source_parser


def add_constructor_parser(parsers: _SubParsersAction,
                           package_parser: ArgumentParser) -> ArgumentParser:

    constructor_parser: ArgumentParser = parsers.add_parser(
        "constructor",
        aliases=["c", "co", "con", "cons", "const", "constr", "constru", "construc"],
        description="interact with the package's source package",
        help="interact with source packages")
    constructor_parser.set_defaults(module="constructor")

    constructor_parsers: _SubParsersAction = constructor_parser.add_subparsers()

    build_parser: ArgumentParser = constructor_parsers.add_parser(
        "build",
        aliases=["b", "bu", "bui", "buil"],
        description="build source packages",
        help="build source packages",
        parents=[package_parser])
    build_parser.add_argument(
        "-m",
        "--message",
        action="store",
        dest="basedir",
        nargs="?",
        help="set changelog message")
    build_parser.set_defaults(module_action="build")

    clean_parser: ArgumentParser = constructor_parsers.add_parser(
        "clean",
        aliases=["c", "cl", "cle", "clea"],
        description="clean up source packages",
        help="clean up source packages",
        parents=[package_parser])
    clean_parser.set_defaults(module_action="clean")

    # lint_parser: ArgumentParser = constructor_parsers.add_parser(
    #     "lint",
    #     aliases=["l", "li", "lin"],
    #     description="lint source packages",
    #     help="lint source packages",
    #     parents=[package_parser])
    # lint_parser.set_defaults(module_action="lint")

    status_parser: ArgumentParser = constructor_parsers.add_parser(
        "status",
        aliases=["s", "st", "sta", "stat", "statu"],
        description="print source package status",
        help="print source package status",
        parents=[package_parser])
    status_parser.set_defaults(module_action="status")

    verify_parser: ArgumentParser = constructor_parsers.add_parser(
        "verify",
        aliases=["v", "ve", "ver", "veri", "verif"],
        description="verify source packages functionality",
        help="verify source packages functionality",
        parents=[package_parser])
    verify_parser.set_defaults(module_action="verify")

    return constructor_parser


def add_builder_parser(parsers: _SubParsersAction,
                       package_parser: ArgumentParser) -> ArgumentParser:

    builder_parser: ArgumentParser = parsers.add_parser(
        "builder",
        aliases=["b", "bu", "bui", "buil", "build", "builde"],
        description="interact with the package's binary packages",
        help="interact with binary packages")
    builder_parser.set_defaults(module="builder")

    builder_parsers: _SubParsersAction = builder_parser.add_subparsers()

    build_parser: ArgumentParser = builder_parsers.add_parser(
        "build",
        aliases=["b", "bu", "bui", "buil"],
        description="build binary packages",
        help="build binary packages",
        parents=[package_parser])
    build_parser.set_defaults(module_action="build")

    clean_parser: ArgumentParser = builder_parsers.add_parser(
        "clean",
        aliases=["c", "cl", "cle", "clea"],
        description="clean up binary packages",
        help="clean up binary packages",
        parents=[package_parser])
    clean_parser.set_defaults(module_action="clean")

    # lint_parser: ArgumentParser = builder_parsers.add_parser(
    #     "lint",
    #     aliases=["l", "li", "lin"],
    #     description="lint binary packages",
    #     help="lint binary packages",
    #     parents=[package_parser])
    # lint_parser.set_defaults(module_action="lint")

    status_parser: ArgumentParser = builder_parsers.add_parser(
        "status",
        aliases=["s", "st", "sta", "stat", "statu"],
        description="print binary package status",
        help="print binary package status",
        parents=[package_parser])
    status_parser.set_defaults(module_action="status")

    verify_parser: ArgumentParser = builder_parsers.add_parser(
        "verify",
        aliases=["v", "ve", "ver", "veri", "verif"],
        description="verify binary packages functionality",
        help="verify binary packages functionality",
        parents=[package_parser])
    verify_parser.set_defaults(module_action="verify")

    return builder_parser


def add_uploader_parser(parsers: _SubParsersAction,
                        package_parser: ArgumentParser) -> ArgumentParser:

    uploader_parser: ArgumentParser = parsers.add_parser(
        "uploader",
        aliases=["u", "up", "upl", "uplo", "uploa"],
        description="interact with a package's uploads",
        help="interact with package uploads")
    uploader_parser.set_defaults(module="uploader")

    uploader_parsers: _SubParsersAction = uploader_parser.add_subparsers()

    clean_parser: ArgumentParser = uploader_parsers.add_parser(
        "clean",
        aliases=["c", "cl", "cle", "clea"],
        description="clean up uploader",
        help="clean up uploader",
        parents=[package_parser])
    clean_parser.set_defaults(module_action="clean")

    status_parser: ArgumentParser = uploader_parsers.add_parser(
        "status",
        aliases=["s", "st", "sta", "stat", "statu"],
        description="print uploader status",
        help="print uploader status",
        parents=[package_parser])
    status_parser.set_defaults(module_action="status")

    upload_parser: ArgumentParser = uploader_parsers.add_parser(
        "upload",
        aliases=["u", "up", "upl", "uplo", "uploa"],
        description="upload packages",
        help="upload packages",
        parents=[package_parser])
    upload_parser.set_defaults(module_action="upload")

    verify_parser: ArgumentParser = uploader_parsers.add_parser(
        "verify",
        aliases=["v", "ve", "ver", "veri", "verif"],
        description="verify upload functionality",
        help="verify upload functionality",
        parents=[package_parser])
    verify_parser.set_defaults(module_action="verify")

    return uploader_parser


def add_pkg_parser(parsers: _SubParsersAction,
                   package_parser: ArgumentParser) -> ArgumentParser:

    pkg_parser: ArgumentParser = parsers.add_parser(
        "package",
        aliases=["p", "pa", "pac", "pack", "packa", "packag"],
        description="interact with packages",
        help="interact with packages")
    pkg_parser.set_defaults(module="package")

    pkg_parsers: _SubParsersAction = pkg_parser.add_subparsers()

    add_parser: ArgumentParser = pkg_parsers.add_parser(
        "add",
        aliases=["a", "ad"],
        description="add package from template",
        help="add package from template",
        parents=[package_parser])
    add_parser.set_defaults(module_action="add")

    clean_parser: ArgumentParser = pkg_parsers.add_parser(
        "clean",
        aliases=["c", "cl", "cle", "clea"],
        description="clean up packages",
        help="clean up packages",
        parents=[package_parser])
    clean_parser.set_defaults(module_action="clean")

    import_parser: ArgumentParser = pkg_parsers.add_parser(
        "import",
        aliases=["i", "im", "imp", "impo", "impor"],
        description="import packages",
        help="import packages",
        parents=[package_parser])
    import_parser.set_defaults(module_action="import")

    status_parser: ArgumentParser = pkg_parsers.add_parser(
        "status",
        aliases=["s", "st", "sta", "stat", "statu"],
        description="print package status",
        help="print package status",
        parents=[package_parser])
    status_parser.set_defaults(module_action="status")

    verify_parser: ArgumentParser = pkg_parsers.add_parser(
        "verify",
        aliases=["v", "ve", "ver", "veri", "verif"],
        description="verify packages",
        help="verify packages",
        parents=[package_parser])
    verify_parser.set_defaults(module_action="verify")

    return pkg_parser


def add_init_parser(parsers: _SubParsersAction) -> ArgumentParser:

    init_parser: ArgumentParser = parsers.add_parser(
        "init",
        aliases=["i", "in", "ini"],
        description="initialize empty kentauros project from template files",
        help="initialize empty kentauros project")
    init_parser.set_defaults(module="init")

    return init_parser


def get_cli_parser() -> ArgumentParser:
    cli_parser = ArgumentParser()
    cli_parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=True,
        default=False,
        help="enable debug output")
    cli_parser.add_argument(
        "-w",
        "--warnings",
        action="store_const",
        const=True,
        default=False,
        help="enable warning messages")
    cli_parser.add_argument(
        "-l",
        "--logfile",
        action="store",
        nargs="?",
        default="",
        help="set kentauros log output file")
    cli_parser.add_argument(
        "-b",
        "--basedir",
        action="store",
        dest="basedir",
        nargs="?",
        default="",
        help="set kentauros project directory")

    parsers = cli_parser.add_subparsers(
        title="modules",
        description="kentauros accepts the sub-commands given below")

    package_parser = ArgumentParser(add_help=False)
    package_parser.add_argument(
        "package",
        action="store",
        nargs="*",
        help="package name").completer = package_name_completer
    package_parser.add_argument(
        "-a", "--all",
        action="store_const",
        dest="packages_all",
        const=True,
        default=False,
        help="apply action to every package with valid configuration")
    package_parser.add_argument(
        "-f", "--force",
        action="store_const",
        const=True,
        default=False,
        help="force actions, even if no updates were available")

    add_init_parser(parsers)
    add_pkg_parser(parsers, package_parser)
    add_source_parser(parsers, package_parser)
    add_constructor_parser(parsers, package_parser)
    add_builder_parser(parsers, package_parser)
    add_uploader_parser(parsers, package_parser)

    return cli_parser
