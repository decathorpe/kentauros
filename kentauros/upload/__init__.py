"""
This subpackage contains the :py:class:`Uploader` base class and
:py:class:`CoprUploader`, which is used for holding information about a
package's upload location or method (if defined in package configuration).
Additionally, this file contains a dictioary which maps :py:class:`UploaderType`
enums to their respective class constructors.
"""

from distutils.util import strtobool
import glob
import os
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import UploaderType
from kentauros.instance import Kentauros, err, log, log_command


LOGPREFIX1 = "ktr/upload: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class Uploader:
    """
    # TODO: napoleon class docstring
    # TODO: move to common.py
    kentauros.upload.Uploader:
    base class for source package uploaders
    """
    def __init__(self, package):
        self.package = package

    def upload(self):
        """
        # TODO: napoleon method docstring
        kentauros.upload.Uploader.upload():
        method that uploads the package
        """
        pass


class CoprUploader(Uploader):
    """
    # TODO: napoleon class docstring
    # TODO: move to copr.py
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


UPLOADER_TYPE_DICT = dict()
# TODO: napoleon variable docstring
UPLOADER_TYPE_DICT[UploaderType.COPR] = CoprUploader
UPLOADER_TYPE_DICT[UploaderType.NONE] = Uploader

