import fcntl
import glob
import grp
import os
import shutil
import time

from .abstract import Builder
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand
from ...validator import KtrValidator

DEFAULT_CFG_PATH = "/etc/mock/default.cfg"
DEFAULT_VAR_PATH = "/var/lib/mock"


class MockCommand(ShellCommand):
    NAME = "mock Command"

    def __init__(self, *args, path: str = None, binary: str = None):
        if binary is None:
            self.exec = "mock"
        else:
            self.exec = binary

        if path is None:
            path = os.getcwd()

        super().__init__(path, self.exec, *args)


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


class MockBuild:
    NAME = "Mock Build"

    def __init__(self, path: str, context: KtrContext, dist: str = None):
        self.path = path
        self.context = context

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

    def name(self):
        return self.NAME

    def get_command(self) -> list:
        cmd = list()

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

        res = MockCommand(*cmd, binary=self.mock).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Mock build was not successful.")
            return ret.submit(False)

        return ret.submit(True)


class MockBuilder(Builder):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.edir = os.path.join(context.get_expodir(), self.package.conf_name)

    def name(self) -> str:
        return "Mock Builder"

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
            ret.messages.err("The current user is not allowed to use mock.")
            ret.messages.err("Add yourself to the 'mock' group, log out and back in.")
            success = False

        if mock_user == "root":
            ret.messages.err("Don't attempt to run mock as root.")
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

    def build(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if not self.get_active():
            return ret.submit(True)

        package_dir = os.path.join(self.context.get_packdir(), self.package.conf_name)

        # get all srpms in the package directory
        srpms = glob.glob(os.path.join(package_dir, self.package.name + "*.src.rpm"))

        if not srpms:
            ret.messages.log("No source packages were found. Construct them first.")
            return ret.submit(False)

        # only build the most recent srpm file
        srpms.sort(reverse=True)
        srpm_path = srpms[0]

        srpm_file = os.path.basename(srpm_path)
        last_file = self.get_last_srpm()

        if srpm_file == last_file:
            force = self.context.get_argument("force")

            if not force:
                ret.messages.log(
                    "This file has already been built. Skipping (add --force to override).")
                return ret.submit(True)

        ret.messages.log("Specified chroots: " + str(" ").join(self.get_dists()))

        # generate build queue
        build_queue = list()

        for dist in self.get_dists():
            build_queue.append(MockBuild(srpm_path, self.context, dist))

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
                ret.messages.log("Build succesful: " + str(build))

        if builds_failure:
            for build in builds_failure:
                ret.messages.log("Build failed: " + str(build))

        if not builds_failure:
            ret.state["mock_last_srpm"] = srpm_file

        return ret.submit(not builds_failure)

    def export(self) -> KtrResult:
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

    def get_last_srpm(self) -> str:
        state = self.context.state.read(self.package.conf_name)

        if "mock_last_srpm" in state.keys():
            return state["mock_last_srpm"]
        else:
            return ""

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

    def lint(self) -> KtrResult:
        # TODO
        return KtrResult(True)

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
