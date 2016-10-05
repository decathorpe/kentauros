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
from kentauros.modules.builder.abstract import Builder


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


def get_mock_cmd() -> str:
    """
    This function tries to determine the correct mock binary path. If somethin is messing with the
    `$PATH` environment variable, it will try to account for that. If mock is not installed (or
    cannot be found within `$PATH`, this function will raise an Exception.

    Raises:
        subprocess.CalledProcessError

    Returns:
        str:    path to the mock binary
    """
    logger = KtrLogger(LOGPREFIX)

    mock_cmd = subprocess.check_output(["which", "mock"]).decode().rstrip("\n")

    # check if the right binary is used or if something is messing up $PATH
    if mock_cmd == "/usr/sbin/mock":
        logger.log("Something is messing with your $PATH variable.", 2)
        mock_cmd = "/usr/bin/mock"

    return mock_cmd


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

        self.edir = os.path.join(Kentauros().conf.get_expodir(), self.bpkg.get_conf_name())

    def __str__(self) -> str:
        return "Mock Builder for Package '" + self.bpkg.get_conf_name() + "'"

    def verify(self) -> bool:
        """
        This method runs several checks to ensure mock builds can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `mock` binary is installed and can be found on the system
        * checks if the current user is allowed to run builds with mock
        * checks if the current user is root (building as root is strongly discouraged)

        Returns:
            bool:   verification success
        """

        logger = KtrLogger(LOGPREFIX)

        success = True

        # check if the configuration file is valid
        expected_keys = ["active", "dists", "export", "keep"]

        for key in expected_keys:
            if key not in self.bpkg.conf["mock"]:
                logger.err("The [mock] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # check if mock is installed
        try:
            subprocess.check_output(["which", "mock"]).decode().rstrip("\n")
        except subprocess.CalledProcessError:
            logger.log("Install mock to use the specified builder.")
            success = False

        # check if the user is in the "mock" group or is root
        mock_group = grp.getgrnam("mock")
        mock_user = os.getenv("USER")

        if mock_user not in mock_group.gr_mem:
            logger.err("The current user is not allowed to use mock.")
            logger.err("Add yourself to the 'mock' group, log out and back in.")
            success = False

        if mock_user == "root":
            logger.err("Don't attempt to run mock as root.")
            success = False

        return success

    def get_active(self):
        """
        Returns:
            bool:   boolean value indicating whether this builder should be active
        """

        return self.bpkg.conf.getboolean("mock", "active")

    def get_dists(self):
        """
        Returns:
            list:   list of chroots that are going to be used for sequential builds
        """

        dists = self.bpkg.conf.get("mock", "dists").split(",")

        if dists == [""]:
            dists = [get_default_mock_dist()]

        return dists

    def get_export(self):
        """
        Returns:
            bool:   boolean value indicating whether this builder should export built packages
        """

        return self.bpkg.conf.getboolean("mock", "export")

    def get_keep(self):
        """
        Returns:
            bool:   boolean value indicating whether this builder should keep source packages
        """

        return self.bpkg.conf.getboolean("mock", "keep")

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

        if not self.get_active():
            return True

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        packdir = os.path.join(ktr.conf.get_packdir(), self.bpkg.get_conf_name())

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(packdir, self.bpkg.get_name() + "*.src.rpm"))

        if not srpms:
            logger.log("No source packages were found. Construct them first.", 2)
            return False

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        logger.log_list("Specified chroots", self.get_dists())

        # generate build queue
        build_queue = list()

        mock_cmd = get_mock_cmd()

        for dist in self.get_dists():
            build_queue.append(MockBuild(mock_cmd, srpm, dist))

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
        if not self.get_keep():
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

        if not self.get_active():
            return True

        if not self.get_export():
            return True

        logger = KtrLogger(LOGPREFIX)

        os.makedirs(self.edir, exist_ok=True)

        if not os.path.exists(self.edir):
            logger.err("Package exports directory could not be created.")
            return False

        if not os.access(self.edir, os.W_OK):
            logger.err("Package exports directory can not be written to.")
            return False

        mock_result_dirs = list()

        for dist in self.get_dists():
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
            shutil.copy2(file, self.edir)

        return True

    def execute(self) -> bool:
        logger = KtrLogger(LOGPREFIX)

        success = self.build()

        if not success:
            logger.log("Binary package building unsuccessful, aborting action.")
            return False

        success = self.export()

        if not success:
            logger.log("Binary package exporting unsuccessful, aborting action.")
            return False

        return success

    def clean(self) -> bool:
        if not os.path.exists(self.edir):
            return True

        logger = KtrLogger(LOGPREFIX)

        try:
            assert Kentauros().conf.get_expodir() in self.edir
            assert os.path.isabs(self.edir)
            shutil.rmtree(self.edir)
            return True
        except AssertionError:
            logger.err("The Package exports directory looks weird. Doing nothing.")
            return False
        except OSError:
            logger.err("The Package exports directory couldn't be removed.")
            return False
