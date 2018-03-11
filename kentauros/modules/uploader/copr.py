import glob
import logging
import os

from kentauros.conntest import is_connected
from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from kentauros.result import KtrResult
from kentauros.shell_env import ShellEnv
from kentauros.validator import KtrValidator
from .abstract import Uploader

DEFAULT_COPR_URL = "https://copr.fedorainfracloud.org"


class CoprUploader(Uploader):
    NAME = "COPR Uploader"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.remote = DEFAULT_COPR_URL

        self.logger = logging.getLogger("ktr/uploader/copr")

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

    def get_last_srpm(self) -> str:
        state = self.context.state.read(self.package.conf_name)

        if "copr_last_srpm" in state.keys():
            return state["copr_last_srpm"]
        else:
            return ""

    def upload(self) -> KtrResult:
        ret = KtrResult()

        if not self.get_active():
            return ret.submit(True)

        package_dir = os.path.join(self.context.get_packdir(), self.package.conf_name)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(package_dir, self.package.name + "*.src.rpm"))

        if not srpms:
            self.logger.error("No source packages were found. Construct them first.")
            return ret.submit(False)

        # only upload the most recent srpm file
        srpms.sort(reverse=True)
        srpm_path = srpms[0]

        srpm_file = os.path.basename(srpm_path)
        last_file = self.get_last_srpm()

        if srpm_file == last_file:
            force = self.context.get_force()

            if not force:
                self.logger.info("This file has already been uploaded. Skipping.")
                return ret.submit(True)

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
        cmd.append(srpm_path)

        # check for connectivity to server
        if not is_connected(self.remote):
            self.logger.error("No connection to remote host detected. Cancelling upload.")
            return ret.submit(False)

        self.logger.debug(" ".join(cmd))

        with ShellEnv() as env:
            res = env.execute(*cmd)
        ret.collect(res)

        if not res.success:
            self.logger.error("copr-cli command did not complete successfully.")
            return ret.submit(False)

        if not self.get_keep():
            os.remove(srpm_path)

        # save the last successfully uploaded srpm file
        ret.state["copr_last_srpm"] = srpm_file

        return ret.submit(True)

    def execute(self) -> KtrResult:
        return self.upload()

    def clean(self) -> KtrResult:
        return KtrResult(True)
