"""
# TODO: napoleon module docstring
"""


import glob
import os
import subprocess

from kentauros.conntest import is_connected
from kentauros.instance import Kentauros, log, log_command

from kentauros.upload.uploader import Uploader


LOGPREFIX1 = "ktr/upload/copr: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class CoprUploader(Uploader):
    """
    # TODO: napoleon class docstring
    kentauros.upload.CoprUploader:
    class for copr package uploader
    """
    def __init__(self, package):
        super().__init__(package)

        if "copr" not in self.package.conf.sections():
            self.package.conf.add_section("copr")
            self.package.conf.set("copr", "active", "false")
            self.package.update_config()

        if "active" not in self.package.conf.options("copr"):
            self.package.conf.set("copr", "active", "false")
            self.package.update_config()

        # if copr-cli is not installed: decativate copr uploader in conf file
        try:
            subprocess.check_output(["which", "copr-cli"])
        except subprocess.CalledProcessError:
            self.package.conf.set("copr", "active", "false")
            self.package.update_config()

        self.remote = "https://copr.fedorainfracloud.org"


    def upload(self):
        # TODO: napoleon method docstring

        if not self.package.conf.getboolean("copr", "active"):
            return None

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(Kentauros().conf.packdir,
                                       self.package.name + "*.src.rpm"))

        if srpms == []:
            log(LOGPREFIX1 + "No source packages were found. " + \
                "Construct them first.", 2)
            return None

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        # get dists to build for
        dists = self.package.conf.get("copr", "dist").split(",")
        if dists == "":
            dists = []

        # check for connectivity to server
        if not is_connected(self.remote):
            log("No connection to remote host detected. Cancelling upload.", 2)
            return None

        # construct copr-cli command
        cmd = ["copr-cli"]

        if Kentauros().debug:
            cmd.append("--debug")

        # append build command
        cmd.append("build")

        # append copr repo
        cmd.append(self.package.conf.get("copr", "repo"))

        # append chroots (dists)
        for dist in dists:
            cmd.append("--chroot")
            cmd.append(dist)

        # append --nowait if wait=False
        if self.package.conf.getboolean("copr", "wait"):
            cmd.append("--nowait")

        # append package
        cmd.append(srpm)

        log_command(LOGPREFIX1, "copr-cli", cmd, 1)
        subprocess.call(cmd)

        # remove source package if keep=False is specified
        if not self.package.conf.getboolean("copr", "keep"):
            os.remove(srpm)

