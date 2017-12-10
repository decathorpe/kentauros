"""
This module contains the :py:class:`CoprUploader` class, which can be used to upload .src.rpm
packages to `copr <http://copr.fedorainfracloud.org>`_.
"""


import glob
import os
import subprocess

from ...conntest import is_connected
from ...instance import Kentauros
from ...logcollector import LogCollector
from ...result import KtrResult

from .abstract import Uploader

DEFAULT_COPR_URL = "https://copr.fedorainfracloud.org"


class CoprUploader(Uploader):
    """
    This :py:class:`Uploader` subclass implements methods for all stages of uploading source
    packages. At class instantiation, it checks for existence of the `copr-cli` binary. If it is
    not found in `$PATH`, this instance is set to inactive.

    Arguments:
        Package package:    package for which this src.rpm uploader is for

    Attributes:
        bool active:        determines if this instance is active
    """

    NAME = "COPR Uploader"

    def __init__(self, package):
        super().__init__(package)

        self.remote = DEFAULT_COPR_URL

    def __str__(self) -> str:
        return "COPR Uploader for Package '" + self.upkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        """
        This method runs several checks to ensure copr uploads can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `copr-cli` binary is installed and can be found on the system

        Returns:
            bool:   verification success
        """

        logger = LogCollector(self.name())

        success = True

        # check if the configuration file is valid
        expected_keys = ["active", "dists", "keep", "repo", "wait"]

        for key in expected_keys:
            if key not in self.upkg.conf["copr"]:
                logger.err("The [copr] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # check if copr is installed
        try:
            subprocess.check_output(["which", "copr-cli"])
        except subprocess.CalledProcessError:
            logger.log("Install copr-cli to use the specified builder.")
            success = False

        return KtrResult(success, logger)

    def get_active(self):
        """
        Returns:
            bool:   boolean value indicating whether this builder should be active
        """

        return self.upkg.conf.getboolean("copr", "active")

    def get_dists(self):
        """
        Returns:
            list:   list of chroots that are going to be used for sequential builds
        """

        dists = self.upkg.conf.get("copr", "dists").split(",")

        if dists == [""]:
            dists = []

        return dists

    def get_keep(self):
        """
        Returns:
            bool:   boolean value indicating whether this builder should keep source packages
        """

        return self.upkg.conf.getboolean("copr", "keep")

    def get_repo(self):
        """
        Returns:
            str:    name of the repository to upload to
        """

        return self.upkg.conf.get("copr", "repo")

    def get_wait(self):
        """
        Returns:
            bool:   boolean value indicating whether this builder should wait for remote builds
        """

        return self.upkg.conf.getboolean("copr", "wait")

    def status(self) -> dict:
        return dict()

    def status_string(self) -> str:
        return str()

    def imports(self) -> dict:
        return dict()

    def upload(self) -> KtrResult:
        """
        This method executes the upload of the newest SRPM package found in the package directory.
        The invocation of `copr-cli` also includes the chroot settings set in the package
        configuration file.

        Returns:
            bool:       returns *False* if anything goes wrong, *True* otherwise
        """

        if not self.get_active():
            return KtrResult.true()

        ktr = Kentauros()
        logger = LogCollector(self.name())

        package_dir = os.path.join(ktr.get_packdir(), self.upkg.get_conf_name())

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(package_dir, self.upkg.get_name() + "*.src.rpm"))

        if not srpms:
            logger.log("No source packages were found. Construct them first.")
            return KtrResult(False, logger)

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
            logger.log("No connection to remote host detected. Cancelling upload.")
            return KtrResult(False, logger)

        logger.cmd(cmd)
        ret = subprocess.call(cmd)
        success = not ret

        if success:
            if not self.get_keep():
                os.remove(srpm)
        else:
            logger.log("copr-cli command did not complete successfully.")

        return KtrResult(success, logger)

    def execute(self) -> KtrResult:
        return self.upload()

    def clean(self) -> KtrResult:
        return KtrResult.true()
