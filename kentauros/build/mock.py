"""
This module contains the :py:class:`MockBuilder` class, which can be used
to build binary packages from src.rpm packages.
"""


import fcntl
import glob
import grp
import os
import subprocess
import time

from kentauros.instance import Kentauros, log, log_command
from kentauros.build.builder import Builder


LOGPREFIX1 = "ktr/build/mock: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = " " * len(LOGPREFIX1) + "- "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


class MockBuild:
    """
    This helper class is used for the actual execution of mock.

    Arguments:
        str path:   path of the SRPM package that will be built
        str dist:   chroot that the package will be built in

    Attributes:
        str path:   stores the path of the SRPM package that will be built
        str dist:   stores the chroot that the package will be built in
    """

    def __init__(self, path: str, dist: str=None):
        self.path = path
        self.dist = dist

    def get_command(self):
        """
        This method returns the argument list needed by the subprocess method
        call, assembled from dist and path.

        Returns:
            list:   argument list for consumption by subprocess methods
        """

        ktr = Kentauros()

        cmd = ["mock"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # specify chroot if it has been set
        if self.dist is not None:
            cmd.append("-r")
            cmd.append(self.dist)

        # set .src.rpm file path
        cmd.append(self.path)

        return cmd

    def build(self):
        """
        This method starts the mock build (and waits for already running builds
        with the same chroot to finish before that).

        Returns:
            int:    return code of the subprocess call
        """

        dist_path = os.path.join("/var/lib/mock/", self.dist)
        lock_path = os.path.join(dist_path, "buildroot.lock")

        # wait for builds occupying the specified build chroot
        if os.path.isdir(dist_path):
            build_wait = True

            while build_wait:
                lock_file = open(lock_path, "a+")

                try:
                    fcntl.lockf(lock_file.fileno(),
                                fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    log(LOGPREFIX1 +
                        "The specified build chroot is busy, waiting.", 2)
                    time.sleep(120)
                else:
                    build_wait = False
                finally:
                    lock_file.close()

        cmd = self.get_command()
        log_command(LOGPREFIX1, "mock", cmd, 2)

        ret = subprocess.call(cmd)
        return ret


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

        # if mock is not installed: deactivate mock builder in conf file
        try:
            subprocess.check_output(["which", "mock"])
        except subprocess.CalledProcessError:
            self.package.conf.set("mock", "active", "false")
            self.package.update_config()

    def build(self) -> bool:
        # TODO: napoleon method docstring
        if not self.package.conf.getboolean("mock", "active"):
            return True

        # check if user is in the "mock" group
        mock_group = grp.getgrnam("mock")
        mock_user = os.getenv("USER")
        if not ((mock_user in mock_group.gr_mem) or (mock_user == "root")):
            log(LOGPREFIX1 + "This user is not allowed to build in mock.", 2)
            return False

        ktr = Kentauros()

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(ktr.conf.packdir,
                                       self.package.name + "*.src.rpm"))

        if not srpms:
            log(LOGPREFIX1 +
                "No source packages were found. Construct them first.", 2)
            return False

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        # get dists to build for
        dists = self.package.conf.get("mock", "dist").split(",")
        if dists == "":
            dists = []

        if dists:
            log(LOGPREFIX1 + "Specified chroots:", 2)
            for dist in dists:
                log(LOGPREFIX2 + dist, 2)

        # generate build queue
        build_queue = list()

        if not dists:
            build_queue.append(MockBuild(srpm))
        else:
            for dist in dists:
                build_queue.append(MockBuild(srpm, dist))

        # run builds in queue
        build_succ = list()
        build_fail = list()

        for build in build_queue:
            ret = build.build()
            if ret:
                build_fail.append((build.path, build.dist))
            else:
                build_succ.append((build.path, build.dist))

        # remove source package if keep=False is specified
        if not self.package.conf.getboolean("mock", "keep"):
            os.remove(srpm)

        if build_succ:
            log(LOGPREFIX1 + "Build successes:", 2)
            for success in build_succ:
                log(LOGPREFIX2 + str(success), 2)

        if build_fail:
            log(LOGPREFIX1 + "Build failures:", 2)
            for fails in build_fail:
                log(LOGPREFIX2 + str(fails), 2)

        return not build_fail

    def export(self) -> bool:
        """
        # TODO: export resulting packages to kentauros binary package directory
        # TODO: napoleon method docstring
        """
        pass
