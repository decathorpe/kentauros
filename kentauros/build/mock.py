"""
# TODO: napoleon module docstring
"""


import glob
import os
import subprocess

from kentauros.instance import Kentauros, err, log, log_command
from kentauros.build.builder import Builder


LOGPREFIX1 = "ktr/build/mock: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = " " * len(LOGPREFIX1) + "- "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


class MockBuilder(Builder):
    """
    # TODO: napoleon class docstring
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


    def build(self):
        # TODO: napoleon method docstring
        if not self.package.conf.getboolean("mock", "active"):
            return True

        ktr = Kentauros()

        # WARNING: MockBuilder.build() builds !all!
        # name*.src.rpm packages found in PACKDIR
        srpms = glob.glob(os.path.join(Kentauros().conf.packdir,
                                       self.package.name + "*.src.rpm"))

        if srpms == []:
            log(LOGPREFIX1 + \
                "No source packages were found. Construct them first.", 2)
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
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
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
        if not self.package.conf.getboolean("mock", "keep"):
            for srpm in srpms:
                os.remove(srpm)

        if build_fail == []:
            return True
        else:
            err(LOGPREFIX1 + "There are failed builds:")
            for fail in build_fail:
                err(LOGPREFIX2 + str(fail))
            return False
