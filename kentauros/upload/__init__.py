"""
kentauros.upload module
contains classes, methods and functions for uploading packages to build servers
"""

import glob
import os
import subprocess

from kentauros.config import KTR_CONF
from kentauros.init import DEBUG, err, log


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

        if 'copr' not in self.package.conf:
            raise KeyError(self.package.name + ".conf does not have a 'copr' section.")

        if 'active' not in self.package.conf['copr']:
            raise KeyError(self.package.name + ".conf does not have an copr/active key.")


    def upload(self):
        if not self.package.conf['copr']['active']:
            return None

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(KTR_CONF['main']['packdir'],
                                       self.package.name + "*.src.rpm"))

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        dists = self.package.conf['copr']['dist'].split(",")
        if dists == [""]:
            dists = []

        # construct copr-cli command
        cmd = ["copr-cli"]

        if DEBUG:
            cmd.append("--debug")

        # append build command
        cmd.append("build")

        # append copr repo
        cmd.append(self.package.conf['copr']['repo'])

        # append chroots (dists)
        for dist in dists:
            cmd.append("--chroot")
            cmd.append(dist)

        # append --nowait if wait=False
        if self.package.conf['copr']['wait'] == False:
            cmd.append("--nowait")

        # append package
        cmd.append(srpm)

        log("upload: copr-cli command: " + str(cmd), 1)
        subprocess.call(cmd)

        # remove source package if keep=False is specified
        if not self.package.conf['copr']['keep']:
            os.remove(srpm)

