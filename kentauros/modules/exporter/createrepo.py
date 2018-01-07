import glob
import os
import shutil

from .abstract import Exporter
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand
from ...validator import KtrValidator


class CreateRepoCommand(ShellCommand):
    NAME = "createrepo_c Command"

    def __init__(self, *args, path: str = None, binary: str = None):
        if binary is None:
            self.exec = "createrepo_c"
        else:
            self.exec = binary

        if path is None:
            path = os.getcwd()

        super().__init__(path, self.exec, *args)


class CreateRepoExporter(Exporter):
    NAME = "createrepo Exporter"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.pdir = os.path.join(self.context.get_expodir(), self.package.conf_name)

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

        print(repodata_path)
        shutil.rmtree(repodata_path)
        ret.messages.log("repodata directory removed.")

        return ret.submit(True)

    def execute(self) -> KtrResult:
        return self.export()

    def export(self) -> KtrResult:
        ret = KtrResult()

        if self.get_path() != self.pdir:
            for file in glob.glob(os.path.join(self.pdir, "*.rpm")):
                shutil.copy2(file, self.get_path())

        res = CreateRepoCommand("--update", self.get_path()).execute()
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
