import fcntl
import glob
import grp
import logging
import os
import shutil
import time

from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from kentauros.result import KtrResult
from kentauros.shell_env import ShellEnv
from kentauros.validator import KtrValidator
from .abstract import Builder, Build

DEFAULT_CFG_PATH = "/etc/mock/default.cfg"
DEFAULT_VAR_PATH = "/var/lib/mock"


class MockError(Exception):
    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


def get_default_mock_dist() -> str:
    return os.path.basename(os.path.realpath(DEFAULT_CFG_PATH)).replace(".cfg", "")


def get_dist_from_mock_config(dist: str) -> str:
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
    return os.path.join(DEFAULT_VAR_PATH, dist, "result")


class MockBuild(Build):
    NAME = "ktr/builder/mock"

    def __init__(self, context: KtrContext, path: str, dist: str = None):
        super().__init__(path, dist, context)

        mock_path = shutil.which("mock")

        if "/sbin/" in mock_path:
            self.mock = mock_path.replace("/sbin/", "/bin/")
        else:
            self.mock = mock_path

        if dist is None:
            # determine which dist is pointed to by the "default.cfg" link
            self.dist = get_default_mock_dist()
        else:
            self.dist = dist

        self.logger = logging.getLogger(self.NAME)

    def name(self):
        return self.NAME

    def get_command(self) -> list:
        cmd = list()

        # add --quiet depending on settings
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
        ret = KtrResult()

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
                    self.logger.info("The specified build chroot is busy, waiting.")
                    time.sleep(120)
                else:
                    build_wait = False
                finally:
                    lock_file.close()

        cmd = self.get_command()
        self.logger.debug(" ".join(cmd))

        with ShellEnv() as env:
            res = env.execute(self.mock, *cmd)
        ret.collect(res)

        if not res.success:
            self.logger.error("Mock build was not successful.")
            return ret.submit(False)

        return ret.submit(True)


class MockBuilder(Builder):
    NAME = "ktr/builder/mock"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.logger = logging.getLogger(self.NAME)

    def name(self) -> str:
        return self.NAME

    def __str__(self) -> str:
        return "Mock Builder for Package '" + self.package.conf_name + "'"

    def verify(self) -> KtrResult:
        expected_keys = ["active", "dists", "export", "keep"]
        expected_binaries = ["mock"]

        validator = KtrValidator(self.package.conf.conf, "mock", expected_keys, expected_binaries)
        ret = validator.validate()

        # check if the user is in the "mock" group or is root
        mock_group = grp.getgrnam("mock")
        mock_user = os.getenv("USER")

        success = True

        if mock_user not in mock_group.gr_mem:
            self.logger.error("The current user is not allowed to use mock.")
            self.logger.error("Add yourself to the 'mock' group, log out and back in.")
            success = False

        if mock_user == "root":
            self.logger.error("Don't attempt to run mock as root.")
            success = False

        return ret.submit(success)

    def get_active(self) -> bool:
        return self.package.conf.getboolean("mock", "active")

    def get_dists(self) -> list:
        dists = self.package.conf.get("mock", "dists").split(",")

        if dists == [""]:
            dists = [get_default_mock_dist()]

        return dists

    def get_export(self) -> bool:
        return self.package.conf.getboolean("mock", "export")

    def get_keep(self) -> bool:
        return self.package.conf.getboolean("mock", "keep")

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        return KtrResult(True, "")

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def get_last_srpm(self) -> str:
        state = self.context.state.read(self.package.conf_name)

        if "mock_last_srpm" in state.keys():
            return state["mock_last_srpm"]
        else:
            return ""

    def build(self) -> KtrResult:
        ret = KtrResult()

        if not self.get_active():
            return ret.submit(True)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(self.pdir, self.package.name + "*.src.rpm"))

        if not srpms:
            self.logger.info("No source packages were found. Construct them first.")
            return ret.submit(False)

        # only build the most recent srpm file
        srpms.sort(reverse=True)
        srpm_path = srpms[0]

        srpm_file = os.path.basename(srpm_path)
        last_file = self.get_last_srpm()

        if srpm_file == last_file:
            force = self.context.get_force()

            if not force:
                self.logger.info("This file has already been built. Skipping.")
                return ret.submit(True)

        self.logger.info("Specified chroots: " + str(" ").join(self.get_dists()))

        # generate build queue
        build_queue = list()

        for dist in self.get_dists():
            build_queue.append(MockBuild(self.context, srpm_path, dist))

        # run builds in queue
        builds_success = list()
        builds_failure = list()

        for build in build_queue:
            res = build.build()
            if res.success:
                builds_success.append((build.path, build.dist))
            else:
                builds_failure.append((build.path, build.dist))

        # remove source package if keep=False is specified
        if not self.get_keep():
            os.remove(srpm_path)

        if builds_success:
            for build in builds_success:
                self.logger.info("Build succesful: " + str(build))

        if builds_failure:
            for build in builds_failure:
                self.logger.info("Build failed: " + str(build))

        if not builds_failure:
            ret.state["mock_last_srpm"] = srpm_file

        return ret.submit(not builds_failure)

    def export(self) -> KtrResult:
        if not self.get_active():
            return KtrResult(True)

        if not self.get_export():
            return KtrResult(True)

        ret = KtrResult()

        os.makedirs(self.edir, exist_ok=True)

        if not os.path.exists(self.edir):
            self.logger.error("Package exports directory could not be created.")
            return ret.submit(False)

        if not os.access(self.edir, os.W_OK):
            self.logger.error("Package exports directory can not be written to.")
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
        ret = KtrResult()

        res = self.build()
        ret.collect(res)

        if not res.success:
            self.logger.info("Binary package building unsuccessful, aborting action.")
            return ret.submit(False)

        res = self.export()
        ret.collect(res)

        if not res.success:
            self.logger.info("Binary package exporting unsuccessful, aborting action.")
            return ret.submit(False)
        else:
            return ret.submit(True)

    def lint(self) -> KtrResult:
        ret = KtrResult()

        if not os.path.exists(self.edir):
            self.logger.info("No packages have been built yet.")
            return ret.submit(True)

        files = list(os.path.join(self.edir, path) for path in os.listdir(self.edir))

        if not files:
            self.logger.info("No packages have been built yet.")
            return ret.submit(True)

        with ShellEnv() as env:
            res = env.execute("rpmlint", *files, ignore_retcode=True)
        ret.collect(res)

        self.logger.info("rpmlint output: " + res.value)
        return ret.submit(True)
