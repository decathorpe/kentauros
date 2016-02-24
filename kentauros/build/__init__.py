"""
kentauros.build module
contains classes, methods and functions for building packages locally
"""

import glob
import os
import subprocess

from kentauros.config import KTR_CONF
from kentauros.init import DEBUG, VERBY, err, log
from kentauros.source.common import SourceType


class Builder:
    """
    kentauros.build.Builder:
    base class for source package builders
    """
    def __init__(self, package):
        self.package = package

    def build(self):
        """
        kentauros.build.Builder.build():
        method that runs the package build
        """
        pass

    def export(self):
        """
        kentauros.build.Builder.export():
        method that exports built packages
        """
        pass


class MockBuilder(Builder):
    """
    kentauros.build.MockBuilder:
    class for .src.rpm source package preparator
    """
    def __init__(self, package):
        super().__init__(package)


    def get_active(self):
        """
        kentauros.build.MockBuilder.get_active():
        check if mock building is active
        """
        return bool(self.package.conf['mock']['active'])


    def get_dists(self):
        """
        kentauros.build.MockBuilder.get_dists():
        returns list of dists
        """
        dists = self.package.conf['mock']['dist'].split(",")

        if dists == [""]:
            dists = []

        return dists


    def build(self):
        if not self.get_active():
            return True

        # WARNING: MockBuilder.build() builds all name*.src.rpm packages found in PACKDIR
        srpms = glob.glob(os.path.join(KTR_CONF['main']['packdir'],
                                       self.package.name + "*.src.rpm"))

        dists = self.get_dists()

        # construct mock command
        cmd = ["mock"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        build_succ = list()
        build_fail = list()

        if dists == []:
            for dist in dists:
                cmd_new = cmd.copy()
                cmd_new.append("-r")
                cmd_new.append(dist)
                for srpm in srpms:
                    cmd_newest = cmd_new.copy()
                    cmd_newest.append(srpm)
                    log("build: mock command: " + str(cmd_newest), 1)
                    ret = subprocess.call(cmd_newest)
                    if ret:
                        build_fail.append(srpm)
                    else:
                        build_succ.append(srpm)
        else:
            cmd_new = cmd.copy()
            for srpm in srpms:
                cmd_newest = cmd_new.copy()
                cmd_newest.append(srpm)
                log("build: mock command: " + str(cmd_newest), 1)
                ret = subprocess.call(cmd_newest)
                if ret:
                    build_fail.append(srpm)
                else:
                    build_succ.append(srpm)

        if build_fail == []:
            return True
        else:
            err("build: There are failed builds:")
            err("build: " + str(build_fail))
            return False

