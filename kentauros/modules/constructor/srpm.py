import configparser as cp
import glob
import os
import shutil
import tempfile

from .abstract import Constructor
from .rpm import RPMSpec, RPMSpecError, parse_release
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCmd
from ...validator import KtrValidator


class RPMBuild:
    def __init__(self, package_name: str, context: KtrContext):
        self.context = context
        self.package_name = package_name

        self.basepath = tempfile.mkdtemp()

    def rpmbuild_dir(self):
        return os.path.join(self.basepath, "rpmbuild")

    def build_dir(self):
        return os.path.join(self.basepath, "rpmbuild", "BUILD")

    def buildroot_dir(self):
        return os.path.join(self.basepath, "rpmbuild", "BUILDROOT")

    def rpm_dir(self):
        return os.path.join(self.basepath, "rpmbuild", "RPMS")

    def source_dir(self):
        return os.path.join(self.basepath, "rpmbuild", "SOURCES")

    def spec_dir(self):
        return os.path.join(self.basepath, "rpmbuild", "SPECS")

    def spec_path(self):
        return os.path.join(self.spec_dir(), self.package_name + ".spec")

    def srpm_dir(self):
        return os.path.join(self.basepath, "rpmbuild", "SRPMS")

    def init(self) -> KtrResult:
        ret = KtrResult()

        # create $TEMPDIR/rpmbuild
        if not os.path.exists(self.rpmbuild_dir()):
            os.mkdir(self.rpmbuild_dir())

        ret.messages.dbg("Temporary rpmbuild directory created: " + self.rpmbuild_dir())

        # create $TEMPDIR/rpmbuild/{SPECS,SRPMS,SOURCES}
        for directory in [self.spec_dir(), self.srpm_dir(), self.source_dir()]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        ret.messages.dbg("Temporary 'SOURCES', 'SPECS', 'SRPMS' directories created.")

        return ret

    def build(self) -> KtrResult:
        ret = KtrResult()

        # construct rpmbuild command
        cmd = list()

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        cmd.extend(["--define", "_topdir {}".format(self.rpmbuild_dir())])
        cmd.extend(["--define", "_builddir {}".format(self.build_dir())])
        cmd.extend(["--define", "_buildrootdir {}".format(self.buildroot_dir())])
        cmd.extend(["--define", "_rpmdir {}".format(self.rpm_dir())])
        cmd.extend(["--define", "_sourcedir {}".format(self.source_dir())])
        cmd.extend(["--define", "_specdir {}".format(self.spec_dir())])
        cmd.extend(["--define", "_srcrpmdir {}".format(self.srpm_dir())])

        cmd.append("-bs")
        cmd.append(self.spec_path())

        ret.messages.cmd(cmd)

        res = ShellCmd("rpmbuild").command(*cmd).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.lst("rpmbuild command to build the source package was not successful.",
                             res.value.split("\n"))
            return ret.submit(False)

        return ret

    def export(self) -> list:
        return glob.glob(os.path.join(self.srpm_dir(), "*.src.rpm"))

    def cleanup(self) -> KtrResult:
        ret = KtrResult()

        try:
            assert os.path.exists(self.basepath)
            assert os.path.isdir(self.basepath)
        except AssertionError:
            ret.messages.log("The temporary rpmbuild directory isn't present as expected.")
            ret.submit(False)

        shutil.rmtree(self.basepath)
        ret.messages.dbg("Temporary rpmbuild directory '{}' deleted.".format(self.basepath))
        return ret.submit(True)

    def add_source(self, path: str, keep: bool = True) -> KtrResult:
        ret = KtrResult()

        if keep:
            shutil.copy2(path, self.source_dir())
        else:
            shutil.move(path, self.source_dir())

        ret.messages.log("File copied to SOURCES: '{}'".format(path))
        return ret

    def add_spec(self, path: str) -> KtrResult:
        ret = KtrResult()

        shutil.copy2(path, self.spec_dir())

        ret.messages.log("RPM .spec copied to SPECS: '{}'".format(path))
        return ret

    def get_spec(self) -> KtrResult:
        ret = KtrResult()

        try:
            with open(self.spec_path(), "r") as file:
                ret.value = file.read()
            return ret.submit(True)
        except IOError:
            return ret.submit(False)


class SrpmConstructor(Constructor):
    NAME = "SRPM Constructor"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.rpmbuild = RPMBuild(self.package.name, self.context)

        spec_name = self.package.name + ".spec"
        self.spec_path = os.path.join(self.context.get_specdir(), self.package.conf_name, spec_name)

        try:
            self.stype = self.package.conf.get("modules", "source")
        except cp.NoSectionError:
            self.stype = None
        except cp.NoOptionError:
            self.stype = None
        except KeyError:
            self.stype = None

        self.sdir = os.path.join(self.context.get_datadir(), self.package.conf_name)

        self.last_release = None
        self.last_version = None

        # create ./packages/PACKAGE directory
        if not os.path.exists(self.pdir):
            os.makedirs(self.pdir, exist_ok=True)

    def __str__(self) -> str:
        return "SRPM Constructor for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        expected_keys = []
        expected_binaries = ["rpmbuild", "rpmdev-bumpspec", "rpmlint"]
        expected_files = [self.spec_path]

        validator = KtrValidator(self.package.conf.conf, "srpm",
                                 expected_keys, expected_binaries, expected_files, )

        return validator.validate()

    def _get_last_version(self) -> KtrResult:
        ret = KtrResult()

        # package has just been built
        if self.last_version is not None:
            ret.value = self.last_version
            return ret

        saved_state = self.context.state.read(self.package.conf_name)
        spec = RPMSpec(self.spec_path, self.package, self.context)

        # package is present in database and "rpm_last_version" is set:
        if (saved_state is not None) and ("rpm_last_version" in saved_state):
            ret.value = saved_state["rpm_last_version"]
            return ret
        # package has not been built yet or is being imported
        else:
            try:
                ret.value = spec.get_version()
                return ret
            # spec file could not be parsed
            except RPMSpecError:
                return ret.submit(False)

    def _get_last_release(self) -> KtrResult:
        ret = KtrResult()

        # package has just been built
        if self.last_release is not None:
            ret.value = self.last_release
            return ret

        saved_state = self.context.state.read(self.package.conf_name)
        spec = RPMSpec(self.spec_path, self.package, self.context)

        # package is present in database and "rpm_last_release" is set:
        if (saved_state is not None) and ("rpm_last_release" in saved_state):
            ret.value = saved_state["rpm_last_release"]
            return ret
        # package has not been built yet or is being imported
        else:
            try:
                ret.value = spec.get_release()
                return ret
            # spec file could not be parsed
            except RPMSpecError:
                return ret.submit(False)

    def status(self) -> KtrResult:
        ret = KtrResult()

        res = self._get_last_version()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Last version could not be determined correctly.")
            last_version = None
        else:
            last_version = res.value

        res = self._get_last_release()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Last release could not be determined correctly.")
            last_release = None
        else:
            last_release = res.value

        if (last_version is None) or (last_release is None):
            return ret.submit(False)

        ret.state["rpm_last_version"] = self._get_last_version()
        ret.state["rpm_last_release"] = self._get_last_release()

        return ret.submit(True)

    def status_string(self) -> KtrResult:
        ret = KtrResult()

        res = self.status()
        ret.collect(res)

        if res.success:
            last_version = res.state["rpm_last_version"]
            last_release = res.state["rpm_last_release"]
        else:
            ret.messages.log("Last status could not be determined correctly.")
            last_version = "Unavailable"
            last_release = "Unavailable"

        template = """
        SRPM Constructor module:
          Last Version:     {last_version}
          Last Release:     {last_release}
        """

        ret.value = template.format(last_version=last_version, last_release=last_release)
        return ret.submit(True)

    def imports(self) -> KtrResult:
        ret = KtrResult()

        spec = RPMSpec(self.spec_path, self.package, self.context)

        ret.state = dict(rpm_last_release=spec.get_release(),
                         rpm_last_version=spec.get_version())

        return ret

    def _check_source_presence(self) -> KtrResult:
        result = KtrResult()

        # source is a NoSource: nothing to be checked
        if self.stype is None:
            return result.submit(True)

        # source directory is non-existent
        if not os.path.exists(self.sdir):
            result.messages.log("Package source directory does not exist. Aborting.")
            return result.submit(False)

        # get source directory contents
        contents = os.listdir(self.sdir)

        # directory empty: abort
        if not contents:
            result.messages.log("Package source directory is empty. Aborting.")
            return result.submit(False)

        # look for files (directories are not enough)
        file_found = False

        for entry in contents:
            if os.path.isfile(os.path.join(self.sdir, entry)):
                file_found = True

        # files were found
        if file_found:
            return result.submit(True)

        # no files were found
        else:
            result.messages.log("Package source directory contains no files. Aborting.")
            return result.submit(False)

    def _copy_sources(self, keep: bool = True) -> KtrResult:
        result = KtrResult()

        state = self.context.state.read(self.package.conf_name)

        if "source_files" in state:
            sources = state["source_files"]
        else:
            sources = list()

        for entry in os.listdir(self.sdir):
            # never delete secondary source files
            if entry in sources:
                keep_file = keep
            else:
                keep_file = True

            entry_path = os.path.join(self.sdir, entry)
            if os.path.isfile(entry_path):
                result2 = self.rpmbuild.add_source(entry_path, keep_file)
                result.collect(result2)

        return result

    def _get_source_keep(self) -> bool:
        conf = self.package.conf

        if "source" not in conf.get("package", "modules").split(","):
            return True

        source_type: str = conf.get("modules", "source")
        keep: bool = conf.getboolean(source_type, "keep")

        return keep

    def _prepare(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if self.stype is None:
            ret.messages.dbg("This package does not define a source module.")

        else:
            # if source module is defined check if sources are present
            res = self._check_source_presence()
            ret.collect(res)

            if not res.success:
                return ret.submit(False)

        # copy sources to rpmbuild/SOURCES
        if self.stype is not None:
            res = self._copy_sources(self._get_source_keep())
            ret.collect(res)

            if not res.success:
                ret.messages.log("Sources could not be moved / copied successfully.")
                return ret.submit(False)

        # copy package.conf to rpmbuild/SOURCES
        res = self.rpmbuild.add_source(self.package.conf_path)
        ret.collect(res)

        if not res.success:
            ret.messages.log("Package configuration could not be copied successfully.")
            return ret.submit(False)

        # copy .spec file to rpmbuild/SPECS
        res = self.rpmbuild.add_spec(self.spec_path)
        ret.collect(res)

        if not res.success:
            ret.messages.log("RPM .spec file could not be copied successfully.")
            return ret.submit(False)

        return ret.submit(True)

    def _spec_prepare(self):
        ret = KtrResult()

        spec = RPMSpec(self.rpmbuild.spec_path(), self.package, self.context)

        spec.set_variables()
        spec.set_source()

        if int(parse_release(spec.get_release())[0]) == 0:
            spec.set_version()

            res = spec.do_release_bump("Initial package.")
            ret.collect(res)

            if not res.success:
                ret.messages.log("Could not process the .spec file successfully.")
                return ret.submit(False)

        spec.write_to_file(self.rpmbuild.spec_path())

        return ret.submit(True)

    def _spec_build(self) -> KtrResult:
        ret = KtrResult()

        spec = RPMSpec(self.rpmbuild.spec_path(), self.package, self.context)

        old_version = spec.get_version()
        new_version = spec.build_version_string()

        spec.set_version()

        if new_version != old_version:
            spec.do_release_reset()

            res = spec.do_release_bump("Update to version {}.".format(self.package.get_version()))
            ret.collect(res)

            if not res.success:
                ret.messages.log("Could not process the .spec file successfully.")
                return ret.submit(False)

        spec.write_to_file(self.rpmbuild.spec_path())

        return ret.submit(True)

    def _spec_increment(self) -> KtrResult:
        ret = KtrResult()

        spec = RPMSpec(self.rpmbuild.spec_path(), self.package, self.context)

        message = self.context.get_argument("message")

        spec.set_version()

        res = spec.do_release_bump(message)
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not process the .spec file successfully.")
            return ret.submit(False)

        spec.write_to_file(self.rpmbuild.spec_path())

        return ret.submit(True)

    def clean(self) -> KtrResult:
        ret = KtrResult()

        if not os.path.exists(self.pdir):
            return ret.submit(True)

        for file in os.listdir(self.pdir):
            path = os.path.join(self.pdir, file)
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            else:
                ret.messages.log("The 'packages/{}' directory contains an unexpected item.".format(
                    self.package.conf_name))
                return ret.submit(False)

        try:
            os.rmdir(self.pdir)
        except OSError:
            ret.messages.log("The 'packages/{}' directory could not be deleted.".format(
                self.package.conf_name))
            return ret.submit(False)

        return ret.submit(True)

    def _pre_build(self) -> KtrResult:
        ret = KtrResult()

        # initialize rpmbuild directory
        res = self.rpmbuild.init()
        ret.collect(res)

        if not res.success:
            ret.messages.log("rpmbuild directory could not be initialized correctly.")
            return ret.submit(False)

        # populate rpmbuild directory
        res = self._prepare()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not prepare the rpmbuild directory successfuly.")
            return ret.submit(False)

        # parse spec and set version, release, and other variables
        res = self._spec_prepare()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not prepare the rpm .spec file successfully.")
            return ret.submit(False)

        return ret.submit(True)

    def _post_build(self) -> KtrResult:
        ret = KtrResult()

        # get the built file(s) and copy them to ./packages/PACKAGE/
        files = self.rpmbuild.export()

        for file in files:
            shutil.copy2(file, self.pdir)

        # retrieve the .spec file, including Version, Release bumps and new changelog entries
        shutil.copy2(self.spec_path, self.spec_path + ".old")
        shutil.copy2(self.rpmbuild.spec_path(), self.spec_path)

        # clean up the temporary directory
        res = self.rpmbuild.cleanup()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not clean up the rpmbuild directory.")
            return ret.submit(False)

        return ret.submit(True)

    def increment(self) -> KtrResult:
        ret = KtrResult()

        res = self._pre_build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not execute pre-build stage.")
            return ret.submit(False)

        # bump the "Release" tag
        res = self._spec_increment()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not bump the Release tag successfully.")
            return ret.submit(False)

        # build the source package
        res = self.rpmbuild.build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not build the source package successfully.")
            return ret.submit(False)

        res = self._post_build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not execute post-build stage.")
            return ret.submit(False)

        return ret.submit(True)

    def lint(self) -> KtrResult:
        ret = KtrResult()

        files = list(os.path.join(self.pdir, path) for path in os.listdir(self.pdir))

        if not files:
            ret.messages.log("No package has been built yet. Only linting the .spec file.")

        files.append(self.spec_path)

        res = ShellCmd("rpmlint").command(*files).execute(ignore_retcode=True)
        ret.collect(res)

        ret.messages.lst("rpmlint output:", res.value.split("\n"))
        return ret.submit(True)

    def build(self) -> KtrResult:
        ret = KtrResult()

        res = self._pre_build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not execute pre-build stage.")
            return ret.submit(False)

        # bump the "Version" tag and reset the "Release" tag
        res = self._spec_build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not bump the Release tag successfully.")
            return ret.submit(False)

        # build the source package
        res = self.rpmbuild.build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not build the source package successfully.")
            return ret.submit(False)

        res = self._post_build()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Could not execute post-build stage.")
            return ret.submit(False)

        return ret.submit(True)

    def execute(self) -> KtrResult:
        spec = RPMSpec(self.spec_path, self.package, self.context)

        old_version = spec.get_version()
        new_version = spec.build_version_string()

        updated = new_version != old_version
        force = self.context.get_argument("force")

        if force and (not updated):
            return self.increment()
        else:
            return self.build()
