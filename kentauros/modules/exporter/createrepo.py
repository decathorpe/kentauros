import glob
import logging
import os
import shutil

from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from kentauros.result import KtrResult
from kentauros.shell_env import ShellEnv
from kentauros.validator import KtrValidator
from .abstract import Exporter


class CreateRepoExporter(Exporter):
    NAME = "createrepo Exporter"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.pdir = os.path.join(self.context.get_expodir(), self.package.conf_name)
        self.logger = logging.getLogger("ktr/exporter/createrepo")

    def name(self) -> str:
        return self.NAME

    def __str__(self) -> str:
        return "createrepo Exporter for package " + self.package.conf_name

    def get_active(self) -> bool:
        return self.package.conf.getboolean("createrepo", "active")

    def get_path(self) -> str:
        path = self.package.conf.get("createrepo", "path")

        if path == "":
            return self.pdir
        else:
            return path

    def clean(self) -> KtrResult:
        ret = KtrResult()

        repodata_path = os.path.join(self.get_path(), "repodata")

        if not os.path.exists(repodata_path):
            return ret.submit(True)

        shutil.rmtree(repodata_path)
        self.logger.info(f"repodata directory '{repodata_path}' removed.")

        return ret.submit(True)

    def execute(self) -> KtrResult:
        return self.export()

    def export(self) -> KtrResult:
        ret = KtrResult()

        if self.get_path() != self.pdir:
            for file in glob.glob(os.path.join(self.pdir, "*.rpm")):
                shutil.copy2(file, self.get_path())

        with ShellEnv() as env:
            res = env.execute("createrepo_c", "--update", self.get_path())
        ret.collect(res)

        return ret

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        return KtrResult(True)

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def verify(self) -> KtrResult:
        expected_keys = ["active", "path"]
        expected_binaries = ["createrepo_c"]

        validator = KtrValidator(self.package.conf.conf, "createrepo",
                                 expected_keys, expected_binaries)

        return validator.validate()
