import glob
import logging
import os

from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from kentauros.result import KtrResult
from kentauros.shell_env import ShellEnv
from kentauros.validator import KtrValidator
from .abstract import Builder, Build


class KojiBuild(Build):
    NAME = "koji scratch Build"

    def name(self) -> str:
        return self.NAME

    def get_command(self) -> list:
        cmd = list()

        # add --quiet depending on settings
        if not self.context.debug:
            cmd.append("--quiet")

        # add arguments for scratch builds
        cmd.append("build")
        cmd.append("--scratch")

        # set the target name
        cmd.append(self.dist)

        # set .src.rpm file path
        cmd.append(self.path)

        return cmd

    def build(self) -> KtrResult:
        ret = KtrResult()
        logger = logging.getLogger("ktr/builder/koji-scratch")

        cmd = self.get_command()
        logger.debug(" ".join(cmd))

        with ShellEnv() as env:
            res = env.execute("koji", *cmd)
        ret.collect(res)

        if not res.success:
            logger.error("koji scratch build was not successful.")
            return ret.submit(False)

        for line in res.value.split("\n"):
            if "Created task: " in line:
                ret.value = line.replace("Created task: ", "")
                return ret.submit(True)

        logger.error("koji scratch build output could not be parsed.")
        return ret.submit(False)


class KojiScratchBuilder(Builder):
    NAME = "ktr/builder/koji-scratch"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.task_ids = list()
        self.logger = logging.getLogger(self.NAME)

    def name(self) -> str:
        return self.NAME

    def __str__(self) -> str:
        return f"koji scratch builder for package '{self.package.conf_name}'"

    def verify(self) -> KtrResult:
        expected_keys = ["active", "dists", "export", "keep"]
        expected_binaries = ["koji"]

        validator = KtrValidator(self.package.conf.conf, "kojiscratch",
                                 expected_keys, expected_binaries)

        return validator.validate()

    def get_active(self) -> bool:
        return self.package.conf.getboolean("kojiscratch", "active")

    def get_dists(self) -> list:
        dists = self.package.conf.get("kojiscratch", "dists").split(",")

        if dists == [""]:
            dists = []

        return dists

    def get_export(self) -> bool:
        return self.package.conf.getboolean("kojiscratch", "export")

    def get_keep(self) -> bool:
        return self.package.conf.getboolean("kojiscratch", "keep")

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        return KtrResult(True, "")

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def get_last_srpm(self) -> str:
        state = self.context.state.read(self.package.conf_name)

        if "koji_last_srpm" in state.keys():
            return state["koji_last_srpm"]
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
            build_queue.append(KojiBuild(srpm_path, self.context, dist))

        # run builds in queue
        builds_success = list()
        builds_failure = list()

        for build in build_queue:
            res = build.build()
            if res.success:
                builds_success.append((build.path, build.dist))
                self.task_ids.append(res.value())
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
            ret.state["koji_last_srpm"] = srpm_file

        return ret.submit(not builds_failure)

    def export(self) -> KtrResult:
        ret = KtrResult()

        for task_id in self.task_ids:
            with ShellEnv(self.edir) as env:
                res = env.execute("koji", "download-task", "--noprogress", task_id,
                                  ignore_retcode=True)
            ret.collect(res)

        return ret

    def execute(self) -> KtrResult:
        ret = KtrResult()

        res = self.build()
        ret.collect(res)

        if not res.success:
            self.logger.error("Binary package building unsuccessful, aborting action.")
            return ret.submit(False)

        res = self.export()
        ret.collect(res)

        if not res.success:
            self.logger.error("Binary package exporting unsuccessful, aborting action.")
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

        self.logger.info("rpmlint output:" + res.value)
        return ret.submit(True)
