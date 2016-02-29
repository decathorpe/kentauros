"""
kentauros.build module
contains classes, methods and functions for building packages locally
"""

from distutils.util import strtobool
import glob
import os
import subprocess

from kentauros.config import KTR_CONF
from kentauros.definitions import SourceType, BuilderType
from kentauros.init import DEBUG, VERBY, err, log, log_command


LOGPREFIX1 = "ktr/build: "
LOGPREFIX2 = "           - "


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

        # deactivate mock if section is not present in config file
        if "mock" not in self.package.conf.sections():
            self.package.conf.add_section("mock")
            self.package.conf.set("mock", "active", "false")
            self.package.update_config()

        if "active" not in self.package.conf.options("mock"):
            self.package.conf.set("mock", "active", "false")
            self.package.update_config()

        # if mock is not installed: decativate mock builder in conf file
        try:
            subprocess.check_output(["which", "mock"])
        except subprocess.CalledProcessError:
            self.package.conf.set("mock", "active", "false")
            self.package.update_config()


    def build(self): # pylint: disable=too-many-branches
        if not self.package.conf.getboolean("mock", "active"):
            return True

        # WARNING: MockBuilder.build() builds all name*.src.rpm packages found in PACKDIR
        srpms = glob.glob(os.path.join(KTR_CONF.get("main", "packdir"),
                                       self.package.name + "*.src.rpm"))

        if srpms == []:
            log(LOGPREFIX1 + "No source packages were found. Construct them first.", 2)
            return False

        log(LOGPREFIX1 + "list of found source packages:", 2)
        for srpm in srpms:
            log(LOGPREFIX2 + srpm)

        dists = self.package.conf.get("mock", "dist").split(",")

        if dists != []:
            log(LOGPREFIX1 + "list of specified chroots:", 2)
            for dist in dists:
                log(LOGPREFIX2 + dist, 2)

        # construct mock command
        cmd = ["mock"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        build_succ = list()
        build_fail = list()

        mock_cmds = list()

        if dists != []:
            for dist in dists:
                cmd_new = cmd.copy()
                cmd_new.append("-r")
                cmd_new.append(dist)
                for srpm in srpms:
                    cmd_newest = cmd_new.copy()
                    cmd_newest.append(srpm)
                    mock_cmds.append(cmd_newest)
        else:
            cmd_new = cmd.copy()
            for srpm in srpms:
                cmd_newest = cmd_new.copy()
                cmd_newest.append(srpm)
                mock_cmds.append(cmd_newest)

        for mock_cmd in mock_cmds:
            log_command(LOGPREFIX1, "mock", mock_cmd, 1)
            ret = subprocess.call(mock_cmd)
            if ret:
                build_fail.append(mock_cmd)
            else:
                build_succ.append(mock_cmd)

        # remove source package if keep=False is specified
        if not bool(strtobool(self.package.conf.get("mock", "keep"))):
            for srpm in srpms:
                os.remove(srpm)

        if build_fail == []:
            return True
        else:
            err(LOGPREFIX1 + "There are failed builds:")
            for fail in build_fail:
                err(LOGPREFIX2 + str(fail))
            return False


BUILDER_TYPE_DICT = dict()
BUILDER_TYPE_DICT[BuilderType.MOCK] = MockBuilder

