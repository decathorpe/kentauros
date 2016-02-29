"""
kentauros.upload module
contains classes, methods and functions for uploading packages to build servers
"""

from distutils.util import strtobool
import glob
import os
import subprocess

from kentauros.config import KTR_CONF
from kentauros.definitions import UploaderType
from kentauros.init import DEBUG, err, log, log_command


LOGPREFIX1 = "ktr/upload: "


class Uploader:
    """
    kentauros.upload.Uploader:
    base class for source package uploaders
    """
    def __init__(self, package):
        self.package = package

    def upload(self):
        """
        kentauros.upload.Uploader.upload():
        method that uploads the package
        """
        pass


class CoprUploader(Uploader):
    """
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


    def get_active(self):
        """
        kentauros.upload.CoprUploader.get_active():
        check if copr uploading is active
        """
        return bool(strtobool(self.package.conf['copr']['active']))


    def get_dists(self):
        """
        kentauros.upload.CoprUploader.get_dists():
        returns list of dists
        """
        dists = self.package.conf['copr']['dist'].split(",")

        if dists == [""]:
            dists = []

        return dists


    def get_keep(self):
        """
        kentauros.upload.CoprUploader.get_keep():
        check if srpm should be kept after uploading
        """
        return bool(strtobool(self.package.conf['copr']['keep']))


    def get_repo(self):
        """
        kentauros.upload.CoprUploader.get_repo():
        returns copr repo specified in .conf
        """
        return self.package.conf['copr']['repo']


    def get_wait(self):
        """
        kentauros.upload.CoprUploader.get_wait():
        check if copr-cli should wait for build success or failure
        """
        return bool(strtobool(self.package.conf['copr']['wait']))


    def upload(self):
        if not self.get_active():
            return None

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(KTR_CONF['main']['packdir'],
                                       self.package.name + "*.src.rpm"))

        if srpms == []:
            log(LOGPREFIX1 + "No source packages were found. Construct them first.", 2)
            return False

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        dists = self.get_dists()

        # construct copr-cli command
        cmd = ["copr-cli"]

        if DEBUG:
            cmd.append("--debug")

        # append build command
        cmd.append("build")

        # append copr repo
        cmd.append(self.get_repo())

        # append chroots (dists)
        for dist in dists:
            cmd.append("--chroot")
            cmd.append(dist)

        # append --nowait if wait=False
        if self.get_wait():
            cmd.append("--nowait")

        # append package
        cmd.append(srpm)

        log_command(LOGPREFIX1, "copr-cli", cmd, 1)
        subprocess.call(cmd)

        # remove source package if keep=False is specified
        if not self.get_keep():
            os.remove(srpm)


UPLOADER_TYPE_DICT = dict()
UPLOADER_TYPE_DICT[UploaderType.COPR] = CoprUploader

