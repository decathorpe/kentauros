import configparser as cp
import glob
import os

import argcomplete as ac

from ..context import KtrContext
from ..definitions import PkgModuleType
from ..modules import get_module
from ..package import KtrPackage
from ..task import KtrTask, KtrTaskList

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

    def __init__(self):
        cli_parser = get_cli_parser()

        ac.autocomplete(cli_parser)
        self.args = cli_parser.parse_args()

        # initialise fallback values
        basedir = os.getcwd()
        conf_path = os.path.join(basedir, "kentaurosrc")

        # configuration file is present in cwd
        if os.path.exists("kentaurosrc"):
            conf_path = "kentaurosrc"
            try:
                conf = cp.ConfigParser()
                conf.read(conf_path)
                path = conf.get("main", "basedir")

                if os.path.isabs(path):
                    basedir = path
                else:
                    basedir = os.path.join(os.getcwd(), path)
            except cp.Error:
                basedir = os.getcwd()

        # CLI argument --basedir was specified
        if self.args.basedir != "":
            if os.path.isabs(self.args.basedir):
                basedir = self.args.basedir
            else:
                basedir = os.path.join(os.getcwd(), self.args.basedir)
            conf_path = os.path.join(basedir, "kentauros")

        super().__init__(basedir, conf_path)

        self.debug_flag = self.args.debug
        self.warning_flag = self.args.warnings

    def get_argument(self, key: str):
        if key in vars(self.args).keys():
            return vars(self.args)[key]
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
        if self.args.packages_all:
            pkg_conf_paths = glob.glob(os.path.join(self.get_confdir(), "*.conf"))

            packages = list()
            for pkg_conf_path in pkg_conf_paths:
                packages.append(os.path.basename(pkg_conf_path).replace(".conf", ""))
            packages.sort()
            return packages
        else:
            return self.args.package

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


class KtrCLIRunner:
    def __init__(self):
        self.context = KtrCLIContext()

        conf_names = self.context.get_packages()

        self.task_list = KtrTaskList()

        for conf_name in conf_names:
            package = KtrPackage(self.context, conf_name)

            module_type = self.context.get_module()

            if module_type == PkgModuleType.PACKAGE:
                module_impl = str()
            else:
                module_impl = package.conf.get("modules", str(module_type.name).lower())

            module = get_module(module_type, module_impl.upper(), package, self.context)

            action = self.context.args.module_action

            task = KtrTask(package, module, action, self.context)
            self.task_list.add(task)

    def run(self) -> int:
        result = self.task_list.execute()

        logfile = self.context.args.logfile
        warnings = self.context.warnings()
        debug = self.context.debug()

        if logfile == "":
            result.messages.print(warnings, debug)
        else:
            with open(logfile, "a") as file:
                result.messages.print(dest=file, warnings=warnings, debug=debug)

        if result.success:
            return 0
        else:
            return -1
