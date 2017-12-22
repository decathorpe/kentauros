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

from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...validator import KtrValidator

from .abstract import Builder

DEFAULT_CFG_PATH = "/etc/mock/default.cfg"
DEFAULT_VAR_PATH = "/var/lib/mock"


class MockError(Exception):
    """
    This custom exception will be raised when errors occur during parsing of
    mock configuration files.

    Arguments:
        str value:  informational string accompanying the exception
    """

    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


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

        raise MockError("Invalid configuration file " + cfg_dist + ": " +
                        "It doesn't seem to contain the 'config_opts['root']' option.")


def get_dist_result_path(dist: str) -> str:
    """
    This helper function constructs the mock result path for a given dist string.

    Arguments:
        str dist:   name of the standard dist

    Returns:
        str:        path pointing to the mock result directory for this dist
    """

    return os.path.join(DEFAULT_VAR_PATH, dist, "result")


def get_mock_cmd() -> str:
    """
    This function tries to determine the correct mock binary path. If something is messing with the
    `$PATH` environment variable, it will try to account for that. If mock is not installed (or
    cannot be found within `$PATH`, this function will raise an Exception.

    Raises:
        subprocess.CalledProcessError

    Returns:
        str:    path to the mock binary
    """

    mock_cmd = shutil.which("mock")

    # check if the right binary is used or if something is messing up $PATH
    if mock_cmd == "/usr/sbin/mock":
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

    NAME = "Mock Build"

    def __init__(self, mock: str, path: str, context: KtrContext, dist: str = None):
        self.mock = mock
        self.path = path
        self.context = context

        if dist is None:
            # determine which dist is pointed to by the "default.cfg" link
            self.dist = get_default_mock_dist()
        else:
            self.dist = dist

    def name(self):
        """
        This method returns the module name for generating log messages.

        Returns:
            str:    module name for log messages
        """

        return self.NAME

    def get_command(self) -> list:
        """
        This method returns the argument list needed by the subprocess method call, assembled from
        dist and path.

        Returns:
            list:   argument list for consumption by subprocess methods
        """

        cmd = [self.mock]

        # add --verbose or --quiet depending on settings
        if not self.context.debug:
            cmd.append("--quiet")

        # specify chroot if it has been set
        if self.dist is not None:
            cmd.append("-r")
            cmd.append(self.dist)

        # set .src.rpm file path
        cmd.append(self.path)

        return cmd

    def build(self) -> KtrResult:
        """
        This method starts the mock build (and waits for already running builds with the same
        chroot to finish before that).

        Returns:
            int:    return code of the subprocess call
        """

        ret = KtrResult(name=self.name())

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
                    ret.messages.log("The specified build chroot is busy, waiting.")
                    time.sleep(120)
                else:
                    build_wait = False
                finally:
                    lock_file.close()

        cmd = self.get_command()
        ret.messages.cmd(cmd)

        try:
            res: subprocess.CompletedProcess = subprocess.run(cmd,
                                                              stdout=subprocess.PIPE,
                                                              stderr=subprocess.STDOUT)
            return ret.submit(res.returncode == 0)
        except PermissionError:
            ret.messages.log("Mock build has been cancelled.")
            return ret.submit(False)


class MockBuilder(Builder):
    """
    This :py:class:`Builder` subclass is used to hold information and methods for executing a local
    package build using ``mock``. At class instantiation, it checks for existence of the ``mock``
    binary. If it is not found in ``$PATH``, this instance is set to inactive.

    Arguments:
        Package package:    package for which this mock/srpm builder is for

    Attributes:
        bool active:        determines if this instance is active
    """

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.edir = os.path.join(context.get_expodir(), self.package.conf_name)

    def name(self) -> str:
        return "Mock Builder"

    def __str__(self) -> str:
        return "Mock Builder for Package '" + self.package.conf_name + "'"

    def verify(self) -> KtrResult:
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

        expected_keys = ["active", "dists", "export", "keep"]
        expected_binaries = ["mock"]

        validator = KtrValidator(self.package.conf.conf, "mock", expected_keys, expected_binaries)
        ret = validator.validate()

        # check if the user is in the "mock" group or is root
        mock_group = grp.getgrnam("mock")
        mock_user = os.getenv("USER")

        success = True

        if mock_user not in mock_group.gr_mem:
            ret.messages.err("The current user is not allowed to use mock.")
            ret.messages.err("Add yourself to the 'mock' group, log out and back in.")
            success = False

        if mock_user == "root":
            ret.messages.err("Don't attempt to run mock as root.")
            success = False

        return ret.submit(success)

    def get_active(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether this builder should be active
        """

        return self.package.conf.getboolean("mock", "active")

    def get_dists(self) -> list:
        """
        Returns:
            list:   list of chroots that are going to be used for sequential builds
        """

        dists = self.package.conf.get("mock", "dists").split(",")

        if dists == [""]:
            dists = [get_default_mock_dist()]

        return dists

    def get_export(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether this builder should export built packages
        """

        return self.package.conf.getboolean("mock", "export")

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether this builder should keep source packages
        """

        return self.package.conf.getboolean("mock", "keep")

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        return KtrResult(True, "")

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def build(self) -> KtrResult:
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

        ret = KtrResult(name=self.name())

        if not self.get_active():
            return ret.submit(True)

        package_dir = os.path.join(self.context.get_packdir(), self.package.conf_name)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(package_dir, self.package.name + "*.src.rpm"))

        if not srpms:
            ret.messages.log("No source packages were found. Construct them first.")
            return ret.submit(False)

        # figure out which srpm to build
        srpms.sort(reverse=True)
        srpm = srpms[0]

        ret.messages.log("Specified chroots: " + str(" ").join(self.get_dists()))

        # generate build queue
        build_queue = list()

        mock_cmd = get_mock_cmd()

        for dist in self.get_dists():
            build_queue.append(MockBuild(mock_cmd, srpm, dist))

        # run builds in queue
        builds_success = list()
        builds_failure = list()

        for build in build_queue:
            res = build.build()
            if res.success:
                builds_failure.append((build.path, build.dist))
            else:
                builds_success.append((build.path, build.dist))

        # remove source package if keep=False is specified
        if not self.get_keep():
            os.remove(srpm)

        if builds_success:
            for build in builds_success:
                ret.messages.log("Build succesful: " + str(build))

        if builds_failure:
            for build in builds_failure:
                ret.messages.log("Build failed: " + str(build))

        return ret.submit(not builds_failure)

    def export(self) -> KtrResult:
        """
        This method copies the build results (if any) from the mock result directory to the
        directory specified for binary package exports.

        Returns:
            bool:   *True* if successful, *False* if not
        """

        if not self.get_active():
            return KtrResult(True)

        if not self.get_export():
            return KtrResult(True)

        ret = KtrResult(name=self.name())

        os.makedirs(self.edir, exist_ok=True)

        if not os.path.exists(self.edir):
            ret.messages.err("Package exports directory could not be created.")
            return ret.submit(False)

        if not os.access(self.edir, os.W_OK):
            ret.messages.err("Package exports directory can not be written to.")
            return ret.submit(False)

        mock_result_dirs = list()

        for dist in self.get_dists():
            path = get_dist_result_path(dist)
            if os.path.exists(path):
                mock_result_dirs.append(path)
            else:
                try:
                    corrected_path = get_dist_result_path(get_dist_from_mock_config(dist))
                except MockError:
                    continue
                mock_result_dirs.append(corrected_path)

        file_results = list()

        for result_dir in mock_result_dirs:
            file_results += glob.glob(os.path.join(result_dir, "*.rpm"))

        for file in file_results:
            shutil.copy2(file, self.edir)

        return ret.submit(True)

    def execute(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Binary package building unsuccessful, aborting action.")
            return ret.submit(False)

        res = self.export()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Binary package exporting unsuccessful, aborting action.")
            return ret.submit(False)
        else:
            return ret.submit(True)

    def clean(self) -> KtrResult:
        if not os.path.exists(self.edir):
            return KtrResult(True)

        ret = KtrResult(name=self.name())

        try:
            assert self.context.get_expodir() in self.edir
            assert os.path.isabs(self.edir)
            shutil.rmtree(self.edir)
            return ret.submit(True)
        except AssertionError:
            ret.messages.err("The Package exports directory looks weird. Doing nothing.")
            return ret.submit(False)
        except OSError:
            ret.messages.err("The Package exports directory couldn't be removed.")
            return ret.submit(False)
