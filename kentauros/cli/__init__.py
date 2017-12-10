from argparse import ArgumentParser, _SubParsersAction

from ..init.cli import package_name_completer
from ..definitions import PkgModuleType


def add_source_parser(parsers: _SubParsersAction,
                      package_parser: ArgumentParser) -> ArgumentParser:

    source_parser: ArgumentParser = parsers.add_parser(
        "source",
        aliases=["s", "so", "sou", "sour", "sourc", "src"],
        description="interact with the package's sources",
        help="interact with sources")
    source_parser.set_defaults(module=PkgModuleType.SOURCE)

    source_parsers: _SubParsersAction = source_parser.add_subparsers()

    get_parser: ArgumentParser = source_parsers.add_parser(
        "get",
        aliases=["g", "ge"],
        description="get sources",
        help="get sources",
        parents=[package_parser])
    get_parser.set_defaults(module_action="get")

    update_parser: ArgumentParser = source_parsers.add_parser(
        "update",
        aliases=["u", "up", "upd", "upda", "updat"],
        description="update sources",
        help="update sources",
        parents=[package_parser])
    update_parser.set_defaults(module_action="update")

    export_parser: ArgumentParser = source_parsers.add_parser(
        "export",
        aliases=["e", "ex", "exp", "expo", "expor"],
        description="export sources",
        help="export sources",
        parents=[package_parser])
    export_parser.set_defaults(module_action="export")

    prepare_parser: ArgumentParser = source_parsers.add_parser(
        "prepare",
        aliases=["p", "pr", "pre", "prep", "prepa", "prepar"],
        description="prepare sources",
        help="prepare_sources",
        parents=[package_parser])
    prepare_parser.set_defaults(module_action="prepare")

    clean_parser: ArgumentParser = source_parsers.add_parser(
        "clean",
        aliases=["c", "cl", "cle", "clea"],
        description="clean up sources",
        help="clean up sources",
        parents=[package_parser])
    clean_parser.set_defaults(module_action="clean")

    return source_parser


def add_constructor_parser(parsers: _SubParsersAction,
                           package_parser: ArgumentParser) -> ArgumentParser:

    constructor_parser: ArgumentParser = parsers.add_parser(
        "constructor",
        aliases=["c", "co", "con", "cons", "const", "constr", "constru", "construc"],
        description="interact with the package's source package",
        help="interact with source packages")
    constructor_parser.set_defaults(module=PkgModuleType.CONSTRUCTOR)

    constructor_parsers: _SubParsersAction = constructor_parser.add_subparsers()

    build_parser: ArgumentParser = constructor_parsers.add_parser(
        "build",
        aliases=["b", "bu", "bui", "buil"],
        description="build source packages",
        help="build source packages",
        parents=[package_parser])
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

    return constructor_parser


def add_builder_parser(parsers: _SubParsersAction,
                       package_parser: ArgumentParser) -> ArgumentParser:

    builder_parser: ArgumentParser = parsers.add_parser(
        "builder",
        aliases=["b", "bu", "bui", "buil", "build", "builde"],
        description="interact with the package's binary packages",
        help="interact with binary packages")

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

    return builder_parser


def add_uploader_parser(parsers: _SubParsersAction,
                        package_parser: ArgumentParser) -> ArgumentParser:

    uploader_parser: ArgumentParser = parsers.add_parser(
        "uploader",
        aliases=["u", "up", "upl", "uplo", "uploa"],
        description="interact with a package's uploads",
        help="interact with package uploads")

    uploader_parsers: _SubParsersAction = uploader_parser.add_subparsers()

    upload_parser: ArgumentParser = uploader_parsers.add_parser(
        "upload",
        aliases=["u", "up", "upl", "uplo", "uploa"],
        description="upload packages",
        help="upload packages",
        parents=[package_parser])
    upload_parser.set_defaults(module_action="upload")

    return uploader_parser


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
        const=True,
        default=False,
        help="apply action to every package with valid configuration")
    package_parser.add_argument(
        "-f", "--force",
        action="store_const",
        const=True,
        default=False,
        help="force actions, even if no updates were available")

    add_source_parser(parsers, package_parser)
    add_constructor_parser(parsers, package_parser)
    add_builder_parser(parsers, package_parser)
    add_uploader_parser(parsers, package_parser)

    return cli_parser
