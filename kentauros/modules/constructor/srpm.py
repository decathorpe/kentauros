"""
This module contains the :py:class:`SrpmConstructor` class, which can be used to construct .src.rpm
packages.
"""


import glob
import os
import shutil
import subprocess
import tempfile

from ...instance import Kentauros
from ...result import KtrResult
from ...logcollector import LogCollector

from ..sources.no_source import NoSource

from .abstract import Constructor
from .rpm import RPMSpec, do_release_bump, parse_release


class SrpmConstructor(Constructor):
    """
    This :py:class:`Constructor` subclass implements methods for all stages of building and
    exporting source packages. At class instantiation, it checks for existence of `rpmbuild` and
    `rpmdev-bumpspec` binaries. If they are not found in ``$PATH``, this instance is rendered
    inactive.

    Arguments:
        Package package:    package for which this src.rpm constructor is for

    Attributes:
        bool active:        determines if this instance is active
        str dirs:           dictionary containing some directory paths
    """

    NAME = "SRPM Constructor"

    def __init__(self, package):
        super().__init__(package)

        ktr = Kentauros()

        self.dirs = dict()

        self.path = os.path.join(ktr.get_specdir(),
                                 self.cpkg.get_conf_name(),
                                 self.cpkg.get_name() + ".spec")

        self.source = self.cpkg.get_module("source")
        self.no_source = (self.source is None)

        if self.no_source:
            self.source = NoSource(package)

        self.last_release = None
        self.last_version = None

        self.success = True

    def __str__(self) -> str:
        return "SRPM Constructor for Package '" + self.cpkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        """
        This method runs several checks to ensure srpm builds can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `mock` binary is installed and can be found on the system
        * checks if the current user is allowed to run builds with mock
        * checks if the current user is root (building as root is strongly discouraged)
        * checks if the .spec file is present at the expected location

        Returns:
            bool:   verification success
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        success = True

        # check if the configuration file is valid
        expected_keys = []
        expected_binaries = ["rpmbuild", "rpmdev-bumpspec"]

        for key in expected_keys:
            if key not in self.cpkg.conf["srpm"]:
                logger.err("The [srpm] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # check for .spec file presence
        if not os.path.exists(self.path):
            logger.err("Spec file has not been found at the expected location:")
            logger.err(self.path)
            success = False

        # check if rpmbuild and rpmdev-bumpspec are installed
        for binary in expected_binaries:
            try:
                subprocess.check_output(["which", binary]).decode().rstrip("\n")
            except subprocess.CalledProcessError:
                logger.log("Install " + binary + " to use the srpm constructor.")
                success = False

        return ret.submit(success)

    def _get_last_version(self, spec: RPMSpec, logger: LogCollector) -> str:
        """
        This method tries to read the latest state from the state database - if that is not
        available, the .spec file is parsed as a fallback.

        Arguments:
            RPMSpec spec:   rpm spec object

        Returns:
            str:            last known version
        """

        assert isinstance(spec, RPMSpec)

        ktr = Kentauros()

        saved_state = ktr.state_read(self.cpkg.get_conf_name())

        if saved_state is None:
            logger.dbg("Package " + self.cpkg.get_conf_name() + " not yet in state database.")
            logger.dbg("Falling back to legacy version detection.")
            return spec.get_version()

        if "rpm_last_version" in saved_state:
            return saved_state["rpm_last_version"]

        logger.dbg("Package " + self.cpkg.get_conf_name() + " has never been built before.")

        if "package_version" in saved_state:
            return saved_state["package_version"]

        logger.dbg("Package " + self.cpkg.get_conf_name() + " has no version set in state DB.")
        logger.dbg("Falling back to legacy version detection.")

        return spec.get_version()

    def _get_last_release(self, spec: RPMSpec, logger: LogCollector):
        """
        This method tries to read the latest state from the state database - if that is not
        available, the .spec file is parsed as a fallback.

        Arguments:
            RPMSpec spec:   rpm spec object

        Returns:
            str:            last known release
        """

        assert isinstance(spec, RPMSpec)

        ktr = Kentauros()

        saved_state = ktr.state_read(self.cpkg.get_conf_name())

        if saved_state is None:
            logger.dbg("Package " + self.cpkg.get_conf_name() + " not yet in state database.")
            logger.dbg("Falling back to legacy release detection.")
            return spec.get_release()

        if "rpm_last_release" in saved_state:
            return saved_state["rpm_last_release"]

        logger.dbg("Package " + self.cpkg.get_conf_name() + " has never been built before.")

        logger.dbg("Package " + self.cpkg.get_conf_name() + " has no release set in state DB.")
        logger.dbg("Falling back to legacy release detection.")

        return spec.get_release()

    def status(self) -> KtrResult:
        spec = RPMSpec(self.path, self.source)

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
        spec = RPMSpec(self.path, self.source)

        ret = KtrResult()

        string = ("SRPM constructor module:\n" +
                  "  Last Version:     {}\n".format(self._get_last_version(spec, ret.messages)) +
                  "  Last Release:     {}\n".format(self._get_last_release(spec, ret.messages)))

        ret.value = string
        return ret.submit(True)

    def imports(self) -> KtrResult:
        spec = RPMSpec(self.path, self.source)

        state = dict(rpm_last_release=spec.get_release(),
                     rpm_last_version=spec.get_version())

        return KtrResult(True, state=state)

    def init(self) -> KtrResult:
        """
        This method creates a temporary directory (which is then set to `$HOME` in the
        :py:meth:`SrpmConstructor.build()` method) and other necessary sub-directories (here:
        `SOURCES`, `SRPMS`, `SPECS`).
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        # make sure to finally call self.clean()!
        self.dirs["tempdir"] = tempfile.mkdtemp()

        logger.dbg("Temporary directory " + self.dirs["tempdir"] + " created.")

        self.dirs["rpmbuild_dir"] = os.path.join(self.dirs["tempdir"], "rpmbuild")
        self.dirs["spec_dir"] = os.path.join(self.dirs["tempdir"], "rpmbuild", "SPECS")
        self.dirs["srpm_dir"] = os.path.join(self.dirs["tempdir"], "rpmbuild", "SRPMS")
        self.dirs["source_dir"] = os.path.join(self.dirs["tempdir"], "rpmbuild", "SOURCES")

        # create $TEMPDIR/rpmbuild
        if not os.path.exists(self.dirs["rpmbuild_dir"]):
            os.mkdir(self.dirs["rpmbuild_dir"])

        logger.dbg("Temporary rpmbuild directory created: " + self.dirs["tempdir"])

        # create $TEMPDIR/rpmbuild/{SPECS,SRPMS,SOURCES}
        for directory in [self.dirs["spec_dir"], self.dirs["srpm_dir"], self.dirs["source_dir"]]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        logger.dbg("Temporary 'SOURCES', 'SPECS', 'SRPMS' directories created.")

        return ret.submit(True)

    def _check_source_presence(self, logger: LogCollector) -> bool:
        """
        This method checks if the Source's output directory is present.
        """

        # source is a NoSource
        if self.source.dest is None:
            return True

        # source directory is non-existent
        if not os.path.exists(self.source.sdir):
            logger.log("Package source directory does not exist. Aborting.")
            return False

        # get source directory contents
        contents = os.listdir(self.source.sdir)

        # directory empty: abort
        if not contents:
            logger.log("Package source directory is empty. Aborting.")
            return False

        # look for files (directories are not enough)
        file_found = False

        for entry in contents:
            if os.path.isfile(os.path.join(self.source.sdir, entry)):
                file_found = True

        # no files were found: abort construction
        if not file_found:
            logger.log("Package source directory contains no files. Aborting.")
            return False

        # files found: everything can continue
        else:
            return True

    def _copy_sources(self, logger: LogCollector):
        """
        This method copies all files (not directories) in the sources directory to the
        `rpmbuild/SOURCES` directory.
        """

        for entry in os.listdir(self.source.sdir):
            entry_path = os.path.join(self.source.sdir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.dirs["source_dir"])
                logger.log("File copied to SOURCES: " + entry_path)

    def _cleanup_sources(self, logger: LogCollector):
        """
        This method cleans up the Source's output directory according to settings.
        """

        if not self.source.get_keep():

            # if source is a tarball (or similar) from the beginning:
            if os.path.isfile(self.source.dest):
                os.remove(self.source.dest)

            # otherwise it is in kentauros' standard .tar.gz format:
            else:
                tarballs = glob.glob(os.path.join(self.source.sdir,
                                                  self.cpkg.get_name()) + "*.tar.gz")

                # remove only the newest one to be safe
                tarballs.sort(reverse=True)

                if os.path.isfile(tarballs[0]):
                    assert self.source.sdir in tarballs[0]
                    os.remove(tarballs[0])
                    logger.log("Tarball removed: " + tarballs[0])

    def _copy_configuration(self, logger: LogCollector):
        """
        This method copies the package configuration file to the `rpmbuild/SOURCES` directory in
        case it is included in the package build.
        """

        shutil.copy2(self.cpkg.file, self.dirs["source_dir"])
        logger.log("Package configuration copied to SOURCES: " + self.cpkg.file)

    def _get_old_status(self, logger: LogCollector) -> (str, str):
        """
        This method tries to determine the old Version and Release strings from the best available
        source. If the local state database has not yet been updated with those values, the .spec
        file is parsed as a fallback.

        Returns:
            tuple:      (version, release)
        """

        spec = RPMSpec(self.path, self.source)

        old_version = self._get_last_version(spec, logger)
        old_release = self._get_last_release(spec, logger)

        return old_version, old_release

    def _get_spec_destination(self) -> str:
        """This method calculates the destination of the .spec file in the `rpmbuild/SPECS` dir."""
        return os.path.join(self.dirs["spec_dir"], self.cpkg.get_name() + ".spec")

    def _prepare_spec(self, logger: LogCollector) -> str:
        """
        This method sets the `Version` and `Source0` tags in the template spec file and resets the
        `Release` tag to `0%{dist}` if the version has changed (to the best of the program's
        knowledge). A preamble to the .spec file containing all necessary macros / definitions is
        generated (and returned). Lastly, the spec is exported to the destination file.

        Returns:
            str:        the contents of the .spec preamble
        """

        spec = RPMSpec(self.path, self.source)

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
        """
        This method prints debug information about old and new Version and Release strings.
        """

        assert isinstance(new_version, str)
        assert isinstance(old_version, str)
        assert isinstance(old_release, str)

        logger.dbg("Old Version: " + old_version)
        logger.dbg("New Version: " + new_version)
        logger.dbg("Old Release: " + old_release)

    def _do_initial_build_prep(self, old_release: str, new_spec_path: str) -> KtrResult:
        """
        This method prepares the .spec file for an initial package build.

        Arguments:
            str old_release:        old release string
            str new_spec_path:      path of new .spec file
        """

        assert isinstance(old_release, str)
        assert isinstance(new_spec_path, str)

        ktr = Kentauros()

        message = ktr.cli.get_message()

        if int(parse_release(old_release)[0]) != 0:
            new_rpm_spec = RPMSpec(new_spec_path, self.source)
            new_rpm_spec.do_release_reset()
            new_rpm_spec.write_contents_to_file(new_spec_path)

        if message is None:
            return do_release_bump(new_spec_path, "Initial package.")
        else:
            return do_release_bump(new_spec_path, message)

    @staticmethod
    def _do_packaging_only_build_prep(new_spec_path: str) -> KtrResult:
        """
        This method prepares the .spec file for a packaging-only change.

        Arguments:
            str new_spec_path:      path of new .spec file
        """

        assert isinstance(new_spec_path, str)

        ktr = Kentauros()

        message = ktr.cli.get_message()

        if message is None:
            return do_release_bump(new_spec_path, "Update for packaging changes.")
        else:
            return do_release_bump(new_spec_path, message)

    def _do_snapshot_update_build_prep(self, new_spec_path: str) -> KtrResult:
        """
        This method prepares the .spec file for a snapshot update.

        Arguments:
            str new_spec_path:      path of new .spec file
        """

        assert isinstance(new_spec_path, str)

        new_rpm_spec = RPMSpec(new_spec_path, self.source)
        new_rpm_spec.do_release_reset()
        new_rpm_spec.write_contents_to_file(new_spec_path)

        return do_release_bump(new_spec_path, "Update to latest snapshot.")

    def _do_version_update_build_prep(self, new_spec_path: str) -> KtrResult:
        """
        This method prepares the .spec file for a version update.

        Arguments:
            str new_spec_path:      path of new .spec file
        """

        assert isinstance(new_spec_path, str)

        return do_release_bump(new_spec_path, "Update to version " + self.cpkg.get_version() + ".")

    def _restore_spec_template(self, new_spec_path: str, preamble: str):
        """
        This method restores the original .spec file template (without added preamble, but with
        possibly added changelog entries).

        Args:
            str new_spec_path:      path of the new spec file
            str preamble:           determined preamble string
        """

        assert isinstance(new_spec_path, str)
        assert isinstance(preamble, str)

        new_rpm_spec = RPMSpec(new_spec_path, self.source)

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
        """
        This method handles the package's .spec file.

        Variables containing the old and new Version and Release strings are calculated (from all
        available sources of information, including the old spec file and the local state database).

        A preamble to the spec file is generated based on which macros are expected to be set for
        different types of sources and is prepended to the output .spec file.

        Based on the information about old and new Version and Release strings, whether a VCS update
        triggered this build or the build was forced, the new Version string is generated.

        * The Release string might not change in case there are no changes to the package and a
          simple construct action has been triggered. No changelog entry is added.
        * If the Version string has changed between builds (or it is the first package build), the
          Release is set to 1 and a changelog entry is added to the .spec file.
        * If a package rebuild is forced (by the `--force` CLI argument, the Release is incremented
          by 1 and a changelog message is added to the .spec file.
        * If a build has been triggered because of an updated VCS snapshot, the Release is reset to
          1 and a changelog entry is added. This only works if the state database has all necessary
          information.
        """

        ktr = Kentauros()

        spec = RPMSpec(self.path, self.source)

        new_version = spec.build_version_string()
        old_version, old_release = self._get_old_status(logger)

        force = ktr.cli.get_force()

        # print debug info
        self._print_debug_info(new_version, old_version, old_release, logger)

        # prepare the spec file and get the generated preamble
        preamble = self._prepare_spec(logger)

        # use "rpmdev-bumpspec" to increment release number and create changelog entries:
        new_spec_path = self._get_spec_destination()

        version_changed = old_version != new_version

        # export spec *with* preamble definitions to destination
        new_spec = RPMSpec(new_spec_path, self.source)
        new_spec.export_to_file(new_spec_path)

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
            if self.source.updated:
                self.success = self._do_snapshot_update_build_prep(new_spec_path)

            # Case 1.3: Package ReConstruction only
            # Version did NOT change, construction was NOT forced and sources were NOT updated
            if (not force) and (not self.source.updated):
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
        """
        This method prepares all files necessary for source package assembly.

        Returns:
            bool:           returns `True` if the preparation was successful.
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        if self.no_source:
            logger.dbg("This package does not define a source module.")

        else:
            # if source module is defined check if sources are present
            if not self._check_source_presence(logger):
                return KtrResult(False, logger)

        # copy sources to rpmbuild/SOURCES
        if not self.no_source:
            self._copy_sources(logger)

        # remove tarballs if they should not be kept
        if not self.no_source:
            self._cleanup_sources(logger)

        # copy package.conf to rpmbuild/SOURCES
        self._copy_configuration(logger)

        # copy modified .spec file to rpmbuild/SPECS
        # copy back file with changelog additions and possible Release bump
        success = self._copy_specs_around(logger)

        return ret.submit(success)

    def build(self) -> KtrResult:
        """
        This method executes the actual SRPM package assembly. It sets `$HOME` to the created
        temporary directory and executes `rpmbuild -bs` with the copy of the package spec file in
        `rpmbuild/SPECS`. After that, `$HOME` is reset to the old value.
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        old_home = os.environ['HOME']
        os.environ['HOME'] = self.dirs["tempdir"]

        # construct rpmbuild command
        cmd = ["rpmbuild"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        cmd.append("-bs")
        cmd.append(os.path.join(self.dirs["spec_dir"], self.cpkg.get_name() + ".spec"))

        logger.cmd(cmd)

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        try:
            res.check_returncode()
            success = True
        except subprocess.CalledProcessError:
            success = False
        finally:
            os.environ['HOME'] = old_home

        if not success:
            logger.lst("rpmbuild execution encountered an error:", res.stdout.decode().split("\n"))

        return ret.submit(success)

    def export(self) -> KtrResult:
        """
        This method copies the assembled source packages from `rpmbuild/SRPMS` to the directory for
        built packages as specified in the kentauros configuration. If multiple SRPM packages are
        found, they all are copied.
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        srpms = glob.glob(os.path.join(self.dirs["srpm_dir"], "*.src.rpm"))

        os.makedirs(self.pdir, exist_ok=True)

        for srpm in srpms:
            shutil.copy2(srpm, self.pdir)
            logger.log("File copied: " + srpm)

        return ret.submit(True)

    def cleanup(self) -> KtrResult:
        shutil.rmtree(self.dirs["tempdir"])
        return KtrResult(True)

    def execute(self) -> KtrResult:
        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        # initialize srpm construction
        res = self.init()
        ret.collect(res)

        # prepare srpm construction
        res = self.prepare()
        ret.collect(res)

        if not res.success:
            # clean up temporary directory
            res = self.cleanup()
            ret.collect(res)
            logger.log("Source package assembly unsuccessful.")
            return ret.submit(False)

        # build srpm
        res = self.build()
        ret.collect(res)

        # export built srpm to packages directory
        res = self.export()
        ret.collect(res)

        # clean up temporary directory
        res = self.cleanup()
        ret.collect(res)

        return ret.submit(True)

    def clean(self) -> KtrResult:
        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        if not os.path.exists(self.pdir):
            return ret.submit(True)

        try:
            assert Kentauros().get_packdir() in self.pdir
            assert os.path.isabs(self.pdir)
            shutil.rmtree(self.pdir)
            return ret.submit(True)
        except AssertionError:
            logger.err("The Package exports directory looks weird. Doing nothing.")
            return ret.submit(False)
        except OSError:
            logger.err("The Package exports directory couldn't be removed.")
            return ret.submit(False)
