import glob
import os
import subprocess as sp

from .abstract import Uploader
from ...conntest import is_connected
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...validator import KtrValidator

DEFAULT_COPR_URL = "https://copr.fedorainfracloud.org"


# TODO: use a ShellCommand subclass for copr-cli commands


class CoprUploader(Uploader):
    NAME = "COPR Uploader"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.remote = DEFAULT_COPR_URL

    def __str__(self) -> str:
        return "COPR Uploader for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        expected_keys = ["active", "dists", "keep", "repo", "wait"]
        expected_binaries = ["copr-cli"]

        validator = KtrValidator(self.package.conf.conf, "copr", expected_keys, expected_binaries)

        return validator.validate()

    def get_active(self) -> bool:
        return self.package.conf.getboolean("copr", "active")

    def get_dists(self) -> list:
        dists = self.package.conf.get("copr", "dists").split(",")

        if dists == [""]:
            dists = []

        return dists

    def get_keep(self) -> bool:
        return self.package.conf.getboolean("copr", "keep")

    def get_repo(self) -> str:
        return self.package.conf.get("copr", "repo")

    def get_wait(self) -> bool:
        return self.package.conf.getboolean("copr", "wait")

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        return KtrResult(True, "")

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def upload(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if not self.get_active():
            return ret.submit(True)

        package_dir = os.path.join(self.context.get_packdir(), self.package.conf_name)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(package_dir, self.package.name + "*.src.rpm"))

        if not srpms:
            ret.messages.log("No source packages were found. Construct them first.")
            return ret.submit(False)

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        # construct copr-cli command
        cmd = ["copr-cli", "build", self.get_repo()]

        # append chroots (dists)
        for dist in self.get_dists():
            cmd.append("--chroot")
            cmd.append(dist)

        # append --nowait if wait=False
        if not self.get_wait():
            cmd.append("--nowait")

        # append package
        cmd.append(srpm)

        # check for connectivity to server
        if not is_connected(self.remote):
            ret.messages.log("No connection to remote host detected. Cancelling upload.")
            return ret.submit(False)

        ret.messages.cmd(cmd)
        res = sp.run(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
        success = (res.returncode == 0)

        if success:
            if not self.get_keep():
                os.remove(srpm)
            return ret.submit(True)
        else:
            ret.messages.log("copr-cli command did not complete successfully.")
            return ret.submit(False)

    def execute(self) -> KtrResult:
        return self.upload()

    def clean(self) -> KtrResult:
        return KtrResult(True)
