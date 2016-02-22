"""
kentauros.build module
contains classes, methods and functions for building packages locally
"""

import glob
import os
import subprocess

from kentauros.config import KTR_CONF
from kentauros.init import log
from kentauros.source.common import SourceType


class Builder:
    def __init__(self, package):
        self.package = package

    def build(self):
        pass


class MockBuilder(Builder):
    def __init__(self, package):
        super().__init__(package)


    def build(self):
        srpms = glob.glob(os.path.join(KTR_CONF['main']['packdir'],
                                       self.package.name + "*.src.rpm"))

        dists = self.package.conf['mock']['dist'].split(",")
        if dists == [""]:
            dists = None

        # construct mock command
        cmd = ["mock"]

        if self.package.source.type == SourceType.GIT:
            # define date macro
            cmd.append("--define=date " + \
                       self.package.source.date() + "." + \
                       str(self.package.source.daily))

            # define rev macro
            cmd.append("--define=rev " + \
                       self.package.source.rev()[0:8])

        # TODO: case bzr
        # TODO: case url

        build_succ = list()
        build_fail = list()

        if dists != None:
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

