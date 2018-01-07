import configparser as cp
import glob
import os

import argcomplete as ac

from .parser import get_cli_parser
from ..context import KtrContext


class KtrCLIContext(KtrContext):
    def __init__(self):
        cli_parser = get_cli_parser()

        ac.autocomplete(cli_parser)

        self.parsed_args = cli_parser.parse_args()
        self.args = vars(self.parsed_args)

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
                basedir = os.path.abspath(path)
            except cp.Error:
                basedir = os.getcwd()

        # CLI argument --basedir was specified
        if "basedir" in self.args and self.args.get("basedir") != "":
            basedir = os.path.abspath(self.args.get("basedir"))
            conf_path = os.path.join(basedir, "kentaurosrc")

        # create basedir if it doesn't exist
        if not os.path.exists(basedir):
            os.makedirs(basedir)

        # create an empty config file if none exists
        if not os.path.exists(conf_path):
            with open(conf_path, "w") as file:
                file.write("")

        super().__init__(basedir, conf_path)

        self.debug_flag = self.args.get("debug")
        self.warning_flag = self.args.get("warnings")

    def get_force(self) -> bool:
        if "force" in self.args.keys():
            return self.args.get("force")
        else:
            return False

    def get_logfile(self) -> str:
        if "logfile" in self.args.keys():
            return self.args.get("logfile")
        else:
            return ""

    def get_message(self) -> str:
        if "message" in self.args.keys():
            return self.args.get("message")
        else:
            return ""

    def debug(self) -> bool:
        return self.debug_flag or os.getenv("KTR_DEBUG", False)

    def warnings(self) -> bool:
        return self.warning_flag or os.getenv("KTR_WARNINGS", False)

    def get_module(self) -> str:
        return self.args.get("module")

    def get_module_action(self) -> str:
        return self.args.get("module_action")

    def get_packages(self) -> list:
        if self.args.get("packages_all"):
            pkg_conf_paths = glob.glob(os.path.join(self.get_confdir(), "*.conf"))

            packages = list()
            for pkg_conf_path in pkg_conf_paths:
                packages.append(os.path.basename(pkg_conf_path).replace(".conf", ""))
            packages.sort()
            return packages
        else:
            return self.args.get("package")

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
