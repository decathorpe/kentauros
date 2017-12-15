import os

import argcomplete as ac

from ..context import KtrContext
from ..definitions import PkgModuleType

from .parser import get_cli_parser


class KtrCLIContext(KtrContext):
    """
    This class encapsulates information gathered from the CLI interface. Some values can be
    overridden by environment variables.

    Arguments:
        str basedir:                    base directory of the kentauros project

    Attributes:
        args:                           Namespace object holding parsed CLI
        bool debug_flag:                flag whether debugging is enabled or not
        bool warning_flag:              flag whether warnings are enabled or not
    """

    def __init__(self, basedir: str = None):
        cli_parser = get_cli_parser()

        ac.autocomplete(cli_parser)
        self.args = cli_parser.parse_args()

        if self.args.basedir != "":
            if os.path.isabs(self.args.basedir):
                basedir = self.args.basedir
            else:
                basedir = os.path.join(os.getcwd(), self.args.basedir)

        super().__init__(basedir)

        self.debug_flag = self.args.debug
        self.warning_flag = self.args.warnings

    def get_argument(self, key: str):
        if key in self.args:
            return self.args[key]
        else:
            return None

    def debug(self) -> bool:
        return self.debug_flag or os.getenv("KTR_DEBUG", False)

    def warnings(self) -> bool:
        return self.warning_flag or os.getenv("KTR_WARNINGS", False)

    def get_module(self) -> PkgModuleType:
        return self.args.module

    def get_module_action(self) -> str:
        return self.args.module_action

    def get_packages(self) -> list:
        return self.args.package

    def get_packages_all(self) -> bool:
        return self.args.packages_all

    def get_basedir(self) -> str:
        return self.basedir

    def get_confdir(self) -> str:
        return os.path.join(self.get_basedir(), "configs")

    def get_datadir(self) -> str:
        return os.path.join(self.get_basedir(), "sources")

    def get_expodir(self) -> str:
        return os.path.join(self.get_basedir(), "exports")

    def get_packdir(self) -> str:
        return os.path.join(self.get_basedir(), "packages")

    def get_specdir(self) -> str:
        return os.path.join(self.get_basedir(), "specs")
