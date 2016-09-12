"""
This module contains the :py:class:`CoprUploader` class, which can be used to upload .src.rpm
packages to `copr <http://copr.fedorainfracloud.org>`_.
"""


import glob
import os
import subprocess

from kentauros.conntest import is_connected
from kentauros.instance import Kentauros

from kentauros.upload.upl_abstract import Uploader


LOGPREFIX1 = "ktr/upload/copr: "
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""

DEFAULT_COPR_URL = "https://copr.fedorainfracloud.org"


class CoprUploader(Uploader):
    """
    This :py:class:`Uploader` subclass implements methods for all stages of uploading source
    packages. At class instantiation, it checks for existance of the `copr-cli` binary. If it is
    not found in `$PATH`, this instance is set to inactive.

    Arguments:
        Package package:    package for which this src.rpm uploader is for

    Attributes:
        bool active:        determines if this instance is active
    """

    def __init__(self, package):
        super().__init__(package)

        # if "active" value has not been set in package.conf, set it to false
        if "active" not in self.upkg.conf.options("copr"):
            self.upkg.conf.set("copr", "active", "false")
            self.upkg.update_config()

        self.active = self.upkg.conf.getboolean("copr", "active")

        # if binaries are not installed: mark CoprUploader instance inactive
        try:
            subprocess.check_output(["which", "copr-cli"])
        except subprocess.CalledProcessError:
            Kentauros(LOGPREFIX1).log("Install copr-cli to use the specified uploader.")
            self.active = False

        self.remote = DEFAULT_COPR_URL

    def upload(self) -> bool:
        """
        This method executes the upload of the newest SRPM package found in the package directory.
        The invocation of `copr-cli` also includes the chroot settings set in the package
        configuration file.

        Returns:
            bool:       returns *False* if anything goes wrong, *True* otherwise
        """

        if not self.active:
            return True

        ktr = Kentauros(LOGPREFIX1)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(Kentauros().conf.get_packdir(),
                                       self.upkg.name + "*.src.rpm"))

        if not srpms:
            ktr.log("No source packages were found. Construct them first.")
            return False

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        # get dists to build for
        dists = self.upkg.conf.get("copr", "dist").split(",")
        if dists == [""]:
            dists = []

        # construct copr-cli command
        cmd = ["copr-cli"]

        if Kentauros().debug:
            cmd.append("--debug")

        # append build command
        cmd.append("build")

        # append copr repo
        cmd.append(self.upkg.conf.get("copr", "repo"))

        # append chroots (dists)
        for dist in dists:
            cmd.append("--chroot")
            cmd.append(dist)

        # append --nowait if wait=False
        if not self.upkg.conf.getboolean("copr", "wait"):
            cmd.append("--nowait")

        # append package
        cmd.append(srpm)

        # check for connectivity to server
        if not is_connected(self.remote):
            ktr.log("No connection to remote host detected. Cancelling upload.", 2)
            return False

        ktr.log_command(LOGPREFIX1, "copr-cli", cmd, 1)
        subprocess.call(cmd)

        # TODO: error handling

        # remove source package if keep=False is specified
        if not self.upkg.conf.getboolean("copr", "keep"):
            os.remove(srpm)

        return True
