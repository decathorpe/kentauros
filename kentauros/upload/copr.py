"""
This module contains the :py:class:`CoprUploader` class, which can be used
to upload src.rpm packages to `copr <http://copr.fedorainfracloud.org>`_.
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
    This :py:class:`Uploader` subclass implements methods for all stages of
    uploading source packages. At class instantiation, it checks for existance
    of the ``copr-cli`` binary. If it is not found in ``$PATH``, this instance
    is set to inactive.

    Arguments:
        Package package: package for which this src.rpm uploader is for

    Attributes:
        bool active: determines if this instance is active
    """

    def __init__(self, package):
        super().__init__(package)

        # if "active" value has not been set in package.conf, set it to false
        if "active" not in self.pkg.conf.options("copr"):
            self.pkg.conf.set("copr", "active", "false")
            self.pkg.update_config()

        self.active = self.pkg.conf.getboolean("copr", "active")

        # if binaries are not installed: mark CoprUploader instance inactive
        try:
            subprocess.check_output(["which", "copr-cli"])
        except subprocess.CalledProcessError:
            log(LOGPREFIX1 + \
                "Install copr-cli to use the specified uploader.")
            self.active = False

        self.remote = "https://copr.fedorainfracloud.org"


    def upload(self):
        # TODO: napoleon method docstring

        if not self.active:
            return None

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(Kentauros().conf.packdir,
                                       self.pkg.name + "*.src.rpm"))

        if srpms == []:
            log(LOGPREFIX1 + "No source packages were found. " + \
                "Construct them first.", 2)
            return None

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        # get dists to build for
        dists = self.pkg.conf.get("copr", "dist").split(",")
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
        cmd.append(self.pkg.conf.get("copr", "repo"))

        # append chroots (dists)
        for dist in dists:
            cmd.append("--chroot")
            cmd.append(dist)

        # append --nowait if wait=False
        if self.pkg.conf.getboolean("copr", "wait"):
            cmd.append("--nowait")

        # append package
        cmd.append(srpm)

        log_command(LOGPREFIX1, "copr-cli", cmd, 1)
        subprocess.call(cmd)

        # remove source package if keep=False is specified
        if not self.pkg.conf.getboolean("copr", "keep"):
            os.remove(srpm)

