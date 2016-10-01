"""
This module contains the :py:class:`MockBuilder` class, which can be used to build binary packages
from src.rpm packages.
"""


import fcntl
import glob
import grp
import os
import shutil
import subprocess
import time

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger
from kentauros.modules.builder.bld_abstract import Builder


LOGPREFIX = "ktr/builder/mock"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""

DEFAULT_CFG_PATH = "/etc/mock/default.cfg"
DEFAULT_VAR_PATH = "/var/lib/mock"


def get_default_mock_dist() -> str:
    """
    This helper function tries to figure out which dist is the default one.

    Returns:
        str:    dist string in default format
    """

    return os.path.basename(os.path.realpath(DEFAULT_CFG_PATH)).replace(".cfg", "")


def get_dist_from_mock_config(dist: str) -> str:
    """
    This helper function tries to read the "real" dist string from a custom dist config file.

    Arguments:
        str dist:   name of the custom dist

    Returns:
        str:        name of the underlying "standard" dist
    """

    cfg_dir = os.path.dirname(DEFAULT_CFG_PATH)
    cfg_dist = os.path.join(cfg_dir, dist + ".cfg")

    with open(cfg_dist, "r") as cfg_file:
        for line in cfg_file:
            if "config_opts['root']" in line:
                real_dist = line.replace("config_opts['root'] = ", "").lstrip("'").rstrip("'\n")
                return real_dist

        return None


def get_dist_result_path(dist: str) -> str:
    """
    This helper function cunstructs the mock result path for a given dist string.

    Arguments:
        str dist:   name of the standard dist

    Returns:
        str:        path pointing to the mock result directory for this dist
    """

    return os.path.join(DEFAULT_VAR_PATH, dist, "result")


class MockBuild:
    """
    This helper class is used for the actual execution of mock.

    Arguments:
        str mock:   path of the used mock binary
        str path:   path of the SRPM package that will be built
        str dist:   chroot that the package will be built in

    Attributes:
        str mock:   stores the path of the used mock binary
        str path:   stores the path of the SRPM package that will be built
        str dist:   stores the chroot that the package will be built in
    """

    def __init__(self, mock: str, path: str, dist: str=None):
        self.mock = mock
        self.path = path

        if dist is None:
            # determine which dist is pointed to by the "default.cfg" link
            self.dist = get_default_mock_dist()
        else:
            self.dist = dist

    def get_command(self):
        """
        This method returns the argument list needed by the subprocess method call, assembled from
        dist and path.

        Returns:
            list:   argument list for consumption by subprocess methods
        """

        ktr = Kentauros()

        cmd = [self.mock]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")

        # specify chroot if it has been set
        if self.dist is not None:
            cmd.append("-r")
            cmd.append(self.dist)

        # set .src.rpm file path
        cmd.append(self.path)

        return cmd

    def build(self):
        """
        This method starts the mock build (and waits for already running builds with the same
        chroot to finish before that).

        Returns:
            int:    return code of the subprocess call
        """

        logger = KtrLogger(LOGPREFIX)

        dist_path = os.path.join("/var/lib/mock/", self.dist)
        lock_path = os.path.join(dist_path, "buildroot.lock")

        # wait 2 minutes for builds occupying the specified build chroot
        if os.path.isdir(dist_path):
            build_wait = True

            while build_wait:
                lock_file = open(lock_path, "a+")

                try:
                    fcntl.lockf(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except IOError:
                    logger.log("The specified build chroot is busy, waiting.", 2)
                    time.sleep(120)
                else:
                    build_wait = False
                finally:
                    lock_file.close()

        cmd = self.get_command()
        logger.log_command(cmd)

        ret = subprocess.call(cmd)
        return ret


class MockBuilder(Builder):
    """
    This :py:class:`Builder` subclass is used to hold information and methods for executing a local
    package build using ``mock``. At class instantiation, it checks for existance of the ``mock``
    binary. If it is not found in ``$PATH``, this instance is set to inactive.

    Arguments:
        Package package:    package for which this mock/srpm builder is for

    Attributes:
        bool active:        determines if this instance is active
    """

    def __init__(self, package):
        super().__init__(package)

        logger = KtrLogger(LOGPREFIX)

        # deactivate mock if section is not present in config file
        if "mock" not in self.bpkg.conf.sections():
            self.bpkg.conf.add_section("mock")
            self.bpkg.conf.set("mock", "active", "false")
            self.bpkg.update_config()

        if "active" not in self.bpkg.conf.options("mock"):
            self.bpkg.conf.set("mock", "active", "false")
            self.bpkg.update_config()

        if "export" not in self.bpkg.conf.options("mock"):
            self.bpkg.conf.set("mock", "export", "false")
            self.bpkg.update_config()

        self.active = self.bpkg.conf.getboolean("mock", "active")
        self.exporting = self.bpkg.conf.getboolean("mock", "export")

        self.mock_cmd = None
        # if mock is not installed: deactivate mock builder in conf file
        try:
            self.mock_cmd = subprocess.check_output(["which", "mock"]).decode().rstrip("\n")
        except subprocess.CalledProcessError:
            logger.log("Install mock to use the specified builder.")
            self.active = False

        # check if the right binary is used or if something is messing up $PATH
        if self.mock_cmd == "/usr/sbin/mock":
            logger.log("Something is messing with your $PATH variable.", 2)
            self.mock_cmd = "/usr/bin/mock"

        # get dists to build for
        self.dists = self.bpkg.conf.get("mock", "dist").split(",")
        if self.dists == [""]:
            self.dists = []

    def status(self) -> dict:
        return dict()

    def build(self) -> bool:
        """
        This method constructs the :py:class:`MockBuilder` instances, which contain the commands
        for executing the builds, and executes them in turn. It also checks if the executing user is
        allowed to execute a mock build by checking if ``$USER`` is "root" or if the user is in the
        "mock" group.

        If no source packages are found in the specified directory (``PACKDIR``), the build
        terminates without executing mock. If SRPM packages are found, only the most recent
        (biggest version number, determined just by sorting!) is built, for all specified chroots.

        After the last mock invocation, a list of successful and unsuccessful builds is printed.

        Returns:
            bool:   ``True`` if all builds succeeded, ``False`` if not
        """

        if not self.active:
            return True

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        # check if user is in the "mock" group
        mock_group = grp.getgrnam("mock")
        mock_user = os.getenv("USER")
        if not ((mock_user in mock_group.gr_mem) or (mock_user == "root")):
            logger.log("This user is not allowed to build in mock.", 2)
            return False

        packdir = os.path.join(ktr.conf.get_packdir(), self.bpkg.conf_name)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(packdir, self.bpkg.name + "*.src.rpm"))

        if not srpms:
            logger.log("No source packages were found. Construct them first.", 2)
            return False

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        logger.log_list("Specified chroots", self.dists)

        # generate build queue
        build_queue = list()

        if not self.dists:
            build_queue.append(MockBuild(self.mock_cmd, srpm))
        else:
            for dist in self.dists:
                build_queue.append(MockBuild(self.mock_cmd, srpm, dist))

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
        if not self.bpkg.conf.getboolean("mock", "keep"):
            os.remove(srpm)

        if build_succ:
            logger.log_list("Build successes", build_succ)

        if build_fail:
            logger.log_list("Build failures", build_fail)

        return not build_fail

    def export(self) -> bool:
        """
        This method copies the build results (if any) from the mock result directory to the
        directory specified for binary package exports.

        Returns:
            bool:   *True* if successful, *False* if not
        """

        if not self.active:
            return True

        if not self.exporting:
            return True

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        pkg_expo_dir = os.path.join(ktr.conf.get_expodir(), self.bpkg.conf_name)
        os.makedirs(pkg_expo_dir, exist_ok=True)

        if not os.path.exists(pkg_expo_dir):
            logger.err("Package exports directory could not be created.")
            return False

        if not os.access(pkg_expo_dir, os.W_OK):
            logger.err("Package exports directory can not be written to.")
            return False

        mock_result_dirs = list()

        if not self.dists:
            self.dists = [get_default_mock_dist()]

        for dist in self.dists:
            path = get_dist_result_path(dist)
            if os.path.exists(path):
                mock_result_dirs.append(path)
            else:
                corrected_path = get_dist_result_path(get_dist_from_mock_config(dist))
                mock_result_dirs.append(corrected_path)

        file_results = list()

        for result_dir in mock_result_dirs:
            file_results += glob.glob(os.path.join(result_dir, "*.rpm"))

        for file in file_results:
            shutil.copy2(file, pkg_expo_dir)

        return True
