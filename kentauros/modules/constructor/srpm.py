import configparser as cp
import glob
import os
import shutil
import tempfile

from .abstract import Constructor
from .rpm import RPMSpec, do_release_bump, parse_release
from ...context import KtrContext
from ...logcollector import LogCollector
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand
from ...validator import KtrValidator


class RPMBuildCommand(ShellCommand):
    NAME = "rpmbuild Command"

    def __init__(self, *args, path: str = None, binary: str = None):
        if binary is None:
            self.exec = "rpmbuild"
        else:
            self.exec = binary

        if path is None:
            path = os.getcwd()

        super().__init__(path, self.exec, *args)


class RPMBuild:
    def __init__(self, package_name: str, context: KtrContext):
        self.context = context
        self.package_name = package_name

        self.basepath = tempfile.mkdtemp()

        # construct directory paths
        self.rpmbuild_dir = os.path.join(self.basepath, "rpmbuild")
        self.build_dir = os.path.join(self.basepath, "rpmbuild", "BUILD")
        self.buildroot_dir = os.path.join(self.basepath, "rpmbuild", "BUILDROOT")
        self.rpm_dir = os.path.join(self.basepath, "rpmbuild", "RPMS")
        self.source_dir = os.path.join(self.basepath, "rpmbuild", "SOURCES")
        self.spec_dir = os.path.join(self.basepath, "rpmbuild", "SPECS")
        self.srpm_dir = os.path.join(self.basepath, "rpmbuild", "SRPMS")

    def init(self) -> KtrResult:
        ret = KtrResult()

        # create $TEMPDIR/rpmbuild
        if not os.path.exists(self.rpmbuild_dir):
            os.mkdir(self.rpmbuild_dir)

        ret.messages.dbg("Temporary rpmbuild directory created: " + self.rpmbuild_dir)

        # create $TEMPDIR/rpmbuild/{SPECS,SRPMS,SOURCES}
        for directory in [self.spec_dir, self.srpm_dir, self.source_dir]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        ret.messages.dbg("Temporary 'SOURCES', 'SPECS', 'SRPMS' directories created.")

        return ret

    def build(self) -> KtrResult:
        ret = KtrResult()

        # construct rpmbuild command
        cmd = ["rpmbuild"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        cmd.extend(["--define", "_topdir {}".format(self.rpmbuild_dir)])
        cmd.extend(["--define", "_builddir {}".format(self.build_dir)])
        cmd.extend(["--define", "_buildrootdir {}".format(self.buildroot_dir)])
        cmd.extend(["--define", "_rpmdir {}".format(self.rpm_dir)])
        cmd.extend(["--define", "_sourcedir {}".format(self.source_dir)])
        cmd.extend(["--define", "_specdir {}".format(self.spec_dir)])
        cmd.extend(["--define", "_srcrpmdir {}".format(self.srpm_dir)])

        cmd.append("-bs")
        cmd.append(os.path.join(self.spec_dir, self.package_name + ".spec"))

        ret.messages.cmd(cmd)

        res = RPMBuildCommand(*cmd).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.lst("rpmbuild command to build the source package was not successful.",
                             res.value.split("\n"))
            return ret.submit(False)

        return ret

    def export(self) -> list:
        return glob.glob(os.path.join(self.srpm_dir, "*.src.rpm"))

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
            shutil.copy2(path, self.source_dir)
        else:
            shutil.move(path, self.source_dir)

        ret.messages.log("File copied to SOURCES: '{}'".format(path))

        return ret

    def add_spec(self, path: str) -> KtrResult:
        # TODO: copy spec to self.spec_dir
        pass

    def get_spec(self) -> KtrResult:
        # TODO: get spec with new changelog entries back
        pass


class SrpmConstructor(Constructor):
    NAME = "SRPM Constructor"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.rpmbuild = RPMBuild(self.package.name, self.context)

        conf_file = self.package.name + ".spec"
        self.path = os.path.join(self.context.get_specdir(), self.package.conf_name, conf_file)

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

        self.success = True

    def __str__(self) -> str:
        return "SRPM Constructor for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        expected_keys = []
        expected_binaries = ["rpmbuild", "rpmdev-bumpspec"]
        expected_files = [self.path]

        validator = KtrValidator(self.package.conf.conf, "srpm",
                                 expected_keys, expected_binaries, expected_files, )

        return validator.validate()

    def _get_last_version(self, spec: RPMSpec, logger: LogCollector) -> str:
        assert isinstance(spec, RPMSpec)

        saved_state = self.context.state.read(self.package.conf_name)

        if saved_state is None:
            logger.dbg("Package " + self.package.conf_name + " not yet in state database.")
            logger.dbg("Falling back to legacy version detection.")
            return spec.get_version()

        if "rpm_last_version" in saved_state:
            return saved_state["rpm_last_version"]

        logger.dbg("Package " + self.package.conf_name + " has never been built before.")

        if "package_version" in saved_state:
            return saved_state["package_version"]

        logger.dbg("Package " + self.package.conf_name + " has no version set in state DB.")
        logger.dbg("Falling back to legacy version detection.")

        return spec.get_version()

    def _get_last_release(self, spec: RPMSpec, logger: LogCollector):
        assert isinstance(spec, RPMSpec)

        saved_state = self.context.state.read(self.package.conf_name)

        if saved_state is None:
            logger.dbg("Package " + self.package.conf_name + " not yet in state database.")
            logger.dbg("Falling back to legacy release detection.")
            return spec.get_release()

        if "rpm_last_release" in saved_state:
            return saved_state["rpm_last_release"]

        logger.dbg("Package " + self.package.conf_name + " has never been built before.")

        logger.dbg("Package " + self.package.conf_name + " has no release set in state DB.")
        logger.dbg("Falling back to legacy release detection.")

        return spec.get_release()

    def status(self) -> KtrResult:
        spec = RPMSpec(self.path, self.package, self.context)

        ret = KtrResult()

        if (self.last_version is None) or (self.last_release is None):
            ret.status = dict(rpm_last_release=spec.get_release(),
                              rpm_last_version=spec.get_version())
            return ret.submit(True)
        else:
            ret.status = dict(rpm_last_release=self.last_release,
                              rpm_last_version=self.last_version)
            return ret.submit(True)

    def status_string(self) -> KtrResult:
        spec = RPMSpec(self.path, self.package, self.context)

        ret = KtrResult()

        string = ("SRPM constructor module:\n" +
                  "  Last Version:     {}\n".format(self._get_last_version(spec, ret.messages)) +
                  "  Last Release:     {}\n".format(self._get_last_release(spec, ret.messages)))

        ret.value = string
        return ret.submit(True)

    def imports(self) -> KtrResult:
        spec = RPMSpec(self.path, self.package, self.context)

        state = dict(rpm_last_release=spec.get_release(),
                     rpm_last_version=spec.get_version())

        return KtrResult(True, state=state)

    def _check_source_presence(self, logger: LogCollector) -> bool:
        # source is a NoSource
        if self.stype is None:
            return True

        # source directory is non-existent
        if not os.path.exists(self.sdir):
            logger.log("Package source directory does not exist. Aborting.")
            return False

        # get source directory contents
        contents = os.listdir(self.sdir)

        # directory empty: abort
        if not contents:
            logger.log("Package source directory is empty. Aborting.")
            return False

        # look for files (directories are not enough)
        file_found = False

        for entry in contents:
            if os.path.isfile(os.path.join(self.sdir, entry)):
                file_found = True

        # no files were found: abort construction
        if not file_found:
            logger.log("Package source directory contains no files. Aborting.")
            return False

        # files found: everything can continue
        else:
            return True

    def _copy_sources(self, keep: bool = True) -> KtrResult:
        ret = KtrResult()

        for entry in os.listdir(self.sdir):
            entry_path = os.path.join(self.sdir, entry)
            if os.path.isfile(entry_path):
                res = self.rpmbuild.add_source(entry_path, keep)
                ret.collect(res)

        return ret

    def _get_source_list(self) -> list:
        state = self.context.state.read(self.package.conf_name)

        if "source_files" not in state.keys():
            return []
        else:
            return state["source_files"]

    def _get_source_last(self) -> list:
        state = self.context.state.read(self.package.conf_name)

        if "rpm_last_sources" not in state.keys():
            return []
        else:
            return state["rpm_last_sources"]

    def _get_source_keep(self) -> bool:
        conf = self.package.conf

        if "source" not in conf.get("package", "modules").split(","):
            return False

        source_type: str = conf.get("modules", "source")
        keep: bool = conf.getboolean(source_type, "keep")

        return keep

    def _copy_configuration(self, logger: LogCollector):
        shutil.copy2(self.package.file, self.rpmbuild.source_dir)
        logger.log("Package configuration copied to SOURCES: " + self.package.file)

    def _get_old_status(self, logger: LogCollector) -> (str, str):
        spec = RPMSpec(self.path, self.package, self.context)

        old_version = self._get_last_version(spec, logger)
        old_release = self._get_last_release(spec, logger)

        return old_version, old_release

    def _get_spec_destination(self) -> str:
        return os.path.join(self.rpmbuild.spec_dir, self.package.name + ".spec")

    def _prepare_spec(self, logger: LogCollector) -> str:
        spec = RPMSpec(self.path, self.package, self.context)

        spec.set_version()
        spec.set_source()

        old_version = self._get_old_status(logger)[0]
        new_version = spec.build_version_string()

        # start constructing release string from old release string
        if new_version != old_version:
            spec.do_release_reset()

        # write preamble to new spec file
        res = spec.build_preamble_string()
        if not res.success:
            raise NotImplementedError("The SRPM Constructor can't proceed due to an unknown error.")
        preamble = res.value

        # write the content of the spec file to destination
        spec.write_contents_to_file(self._get_spec_destination())

        return preamble

    @staticmethod
    def _print_debug_info(new_version, old_version, old_release, logger: LogCollector):
        assert isinstance(new_version, str)
        assert isinstance(old_version, str)
        assert isinstance(old_release, str)

        logger.dbg("Old Version: " + old_version)
        logger.dbg("New Version: " + new_version)
        logger.dbg("Old Release: " + old_release)

    def _do_initial_build_prep(self, old_release: str, new_spec_path: str) -> KtrResult:
        assert isinstance(old_release, str)
        assert isinstance(new_spec_path, str)

        if "message" in self.context.arguments():
            message = self.context.arguments()["message"]
        else:
            message = None

        if int(parse_release(old_release)[0]) != 0:
            new_rpm_spec = RPMSpec(new_spec_path, self.package, self.context)
            new_rpm_spec.do_release_reset()
            new_rpm_spec.write_contents_to_file(new_spec_path)

        if message is None:
            return do_release_bump(new_spec_path, self.context, "Initial package.")
        else:
            return do_release_bump(new_spec_path, self.context, message)

    def _do_packaging_only_build_prep(self, new_spec_path: str) -> KtrResult:
        assert isinstance(new_spec_path, str)

        if "message" in self.context.arguments():
            message = self.context.arguments()["message"]
        else:
            message = None

        if message is None:
            return do_release_bump(new_spec_path, self.context, "Update for packaging changes.")
        else:
            return do_release_bump(new_spec_path, self.context, message)

    def _do_snapshot_update_build_prep(self, new_spec_path: str) -> KtrResult:
        assert isinstance(new_spec_path, str)

        new_rpm_spec = RPMSpec(new_spec_path, self.package, self.context)
        new_rpm_spec.do_release_reset()
        new_rpm_spec.write_contents_to_file(new_spec_path)

        return do_release_bump(new_spec_path, self.context, "Update to latest snapshot.")

    def _do_version_update_build_prep(self, new_spec_path: str) -> KtrResult:
        assert isinstance(new_spec_path, str)

        return do_release_bump(new_spec_path,
                               "Update to version " + self.package.get_version() + ".")

    def _restore_spec_template(self, new_spec_path: str, preamble: str):
        assert isinstance(new_spec_path, str)
        assert isinstance(preamble, str)

        new_rpm_spec = RPMSpec(new_spec_path, self.package, self.context)

        self.last_release = new_rpm_spec.get_release()
        self.last_version = new_rpm_spec.get_version()

        # copy new spec file back to ktr/specdir to preserve version tracking,
        # release number and changelog consistency (keep old version once as backup)
        # BUT: remove preamble again, it would break things otherwise
        # Handling the ChangeLog separately (SUSE style?) would be nice here.

        new_rpm_spec.contents = new_rpm_spec.contents.replace(preamble, "")

        if os.path.exists(self.path + ".old"):
            os.remove(self.path + ".old")

        os.rename(self.path, self.path + ".old")
        new_rpm_spec.write_contents_to_file(self.path)

    def _copy_specs_around(self, logger: LogCollector) -> bool:
        spec = RPMSpec(self.path, self.package, self.context)

        new_version = spec.build_version_string()
        old_version, old_release = self._get_old_status(logger)

        if "force" in self.context.arguments():
            force = self.context.arguments()["force"]
        else:
            force = False

        # print debug info
        self._print_debug_info(new_version, old_version, old_release, logger)

        # prepare the spec file and get the generated preamble
        preamble = self._prepare_spec(logger)

        # use "rpmdev-bumpspec" to increment release number and create changelog entries:
        new_spec_path = self._get_spec_destination()

        version_changed = old_version != new_version

        # export spec *with* preamble definitions to destination
        new_spec = RPMSpec(new_spec_path, self.package, self.context)
        new_spec.export_to_file(new_spec_path)

        # get last and next sources list
        rpm_last_sources = self._get_source_last()
        rpm_next_sources = self._get_source_list()

        # ... and check if they're different (indicating that there's been an update)
        updated = (rpm_next_sources != rpm_last_sources)

        # Case 0: Initial package build
        # Old Version is empty or old Release is 0
        if (old_version == "") or (int(parse_release(old_release)[0]) == 0):
            self.success = self._do_initial_build_prep(old_release, new_spec_path)

        # Case 1:
        # Package Version did NOT change
        elif not version_changed:

            # Cases 1.1 and 1.2 can happen at the same time
            # In this case, the "packaging changes" are applied to the spec first, and
            # the "source changes" after that.

            # Case 1.1: Packaging changes
            # Package Version did NOT change but construction was forced (because of spec changes?)
            if force:
                self.success = self._do_packaging_only_build_prep(new_spec_path)

            # Case 1.2: Snapshot update
            # Package Version did NOT change BUT VCS sources were updated
            if updated:
                self.success = self._do_snapshot_update_build_prep(new_spec_path)

            # Case 1.3: Package ReConstruction only
            # Version did NOT change, construction was NOT forced and sources were NOT updated
            if (not force) and (not updated):
                self.success = True

        # Case 2: Version update
        # Package Version DID change
        elif version_changed:
            self.success = self._do_version_update_build_prep(new_spec_path)

        # Case 3: LOGIC ERROR BEEP BOOP BOOP
        else:
            logger.err("Can't figure out what to do. This shouldn't have happened.")
            return False

        if not self.success:
            return False

        self._restore_spec_template(new_spec_path, preamble)

        return True

    def prepare(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if self.stype is None:
            ret.messages.dbg("This package does not define a source module.")

        else:
            # if source module is defined check if sources are present
            if not self._check_source_presence(ret.messages):
                return ret.submit(False)

        # copy sources to rpmbuild/SOURCES
        if self.stype is not None:
            res = self._copy_sources(keep=self._get_source_keep())
            ret.collect(res)

            if not res.success:
                ret.messages.log("Sources could not be moved / copied successfully.")
                return ret.submit(False)

        # copy package.conf to rpmbuild/SOURCES
        self._copy_configuration(ret.messages)

        # copy modified .spec file to rpmbuild/SPECS
        # copy back file with changelog additions and possible Release bump
        success = self._copy_specs_around(ret.messages)

        return ret.submit(ret.success and success)

    def build(self) -> KtrResult:
        return self.rpmbuild.build()

    def export(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        srpms = self.rpmbuild.export()

        os.makedirs(self.pdir, exist_ok=True)

        for srpm in srpms:
            shutil.copy2(srpm, self.pdir)
            ret.messages.log("File copied: " + srpm)

        return ret.submit(True)

    def execute(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        # initialize srpm construction
        res = self.rpmbuild.init()
        ret.collect(res)

        # prepare srpm construction
        res = self.prepare()
        ret.collect(res)

        if not res.success:
            # clean up temporary directory
            res = self.rpmbuild.cleanup()
            ret.collect(res)
            ret.messages.log("Source package assembly unsuccessful.")
            return ret.submit(False)

        # build srpm
        res = self.build()
        ret.collect(res)

        # export built srpm to packages directory
        res = self.export()
        ret.collect(res)

        # clean up temporary directory
        res = self.rpmbuild.cleanup()
        ret.collect(res)

        ret.state["rpm_last_sources"] = self._get_source_list()
        return ret.submit(True)

    def clean(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if not os.path.exists(self.pdir):
            return ret.submit(True)

        try:
            assert self.context.get_packdir() in self.pdir
            assert os.path.isabs(self.pdir)
            shutil.rmtree(self.pdir)
            return ret.submit(True)
        except AssertionError:
            ret.messages.err("The Package exports directory looks weird. Doing nothing.")
            return ret.submit(False)
        except OSError:
            ret.messages.err("The Package exports directory couldn't be removed.")
            return ret.submit(False)
