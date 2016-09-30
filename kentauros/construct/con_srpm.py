"""
This module contains the :py:class:`SrpmConstructor` class, which can be used to construct .src.rpm
packages.
"""


import glob
import os
import shutil
import subprocess
import tempfile
import warnings

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.construct.con_abstract import Constructor
from kentauros.pkgformat.rpm import RPMSpec, do_release_bump


LOGPREFIX = "ktr/construct/srpm"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class SrpmConstructor(Constructor):
    """
    This :py:class:`Constructor` subclass implements methods for all stages of building and
    exporting source packages. At class instantiation, it checks for existance of `rpmbuild` and
    `rpmdev-bumpspec` binaries. If they are not found in ``$PATH``, this instance is rendered
    inactive.

    Arguments:
        Package package:    package for which this src.rpm constructor is for

    Attributes:
        bool active:        determines if this instance is active
        str tempdir:        absolute path of temporary "HOME" directory
        str rpmbdir:        absolute path of ``rpmbuild`` directory
        str specdir:        absolute path of ``rpmbuild/SPECS`` directory
        str srpmdir:        absolute path of ``rpmbuild/SRPMS`` directory
        str srcsdir:        absolute path of ``rpmbuild/SOURCES`` directory
    """

    def __init__(self, package):
        super().__init__(package)

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        self.tempdir = None
        self.rpmbdir = None
        self.specdir = None
        self.srpmdir = None
        self.srcsdir = None

        # if binaries are not installed: mark SrpmConstructor instance inactive
        try:
            self.active = True
            subprocess.check_output(["which", "rpmbuild"])
            subprocess.check_output(["which", "rpmdev-bumpspec"])
        except subprocess.CalledProcessError:
            logger.log("Install rpmdevtools to use the specified constructor.")
            self.active = False

        self.path = os.path.join(ktr.conf.get_specdir(),
                                 self.cpkg.conf_name,
                                 self.cpkg.name + ".spec")

        try:
            self.spec = RPMSpec(self.path, self.cpkg.get_source())
        except FileNotFoundError:
            logger.err("Spec file has not been found at the expected location:")
            logger.err(self.path)
            self.active = False

    def _get_last_version(self, spec: RPMSpec):
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
        logger = KtrLogger(LOGPREFIX)

        saved_state = ktr.state_read(self.cpkg.conf_name)

        if saved_state is None:
            logger.dbg("Package " + self.cpkg.conf_name + " not yet in state database.")
            logger.dbg("Falling back to legacy version detection.")
            old_version = spec.get_version()
        elif "rpm_last_release" not in saved_state:
            logger.dbg("Package " + self.cpkg.conf_name + " has never been built before.")
            old_version = ""
        elif "source_version" not in saved_state:
            logger.dbg("Package " + self.cpkg.conf_name + " has no version set in state database.")
            logger.dbg("Falling back to legacy version detection.")
            old_version = spec.get_version()
        else:
            old_version = saved_state["source_version"]

        return old_version

    def _get_last_release(self, spec: RPMSpec):
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
        logger = KtrLogger(LOGPREFIX)

        saved_state = ktr.state_read(self.cpkg.conf_name)

        if saved_state is None:
            logger.dbg("Package " + self.cpkg.conf_name + " not yet in state database.")
            logger.dbg("Falling back to legacy release detection.")
            old_release = spec.get_release()
        elif "rpm_last_release" not in saved_state:
            logger.dbg("Package " + self.cpkg.conf_name + " has no release set in state database.")
            logger.dbg("Falling back to legacy release detection.")
            old_release = spec.get_release()
        else:
            old_release = saved_state["rpm_last_release"]

        return old_release

    def status(self) -> dict:
        # TODO: return latest RPM release, etc. so it can be stored after builds
        return dict()

    def init(self):
        """
        This method creates a temporary directory (which is then set to `$HOME` in the
        :py:meth:`SrpmConstructor.build()` method) and other necessary subdirectores (here:
        `SOURCES`, `SRPMS`, `SPECS`).
        """

        if not self.active:
            return

        logger = KtrLogger(LOGPREFIX)

        # make sure to finally call self.clean()!
        self.tempdir = tempfile.mkdtemp()

        logger.log("Temporary directory " + self.tempdir + " created.", 1)

        self.rpmbdir = os.path.join(self.tempdir, "rpmbuild")
        self.specdir = os.path.join(self.tempdir, "rpmbuild", "SPECS")
        self.srpmdir = os.path.join(self.tempdir, "rpmbuild", "SRPMS")
        self.srcsdir = os.path.join(self.tempdir, "rpmbuild", "SOURCES")

        # create $TEMPDIR/rpmbuild
        if not os.path.exists(self.rpmbdir):
            os.mkdir(self.rpmbdir)

        logger.log("Temporary rpmbuild directory created: " + self.tempdir, 1)

        # create $TEMPDIR/rpmbuild/{SPECS,SRPMS,SOURCES}
        for directory in [self.specdir, self.srpmdir, self.srcsdir]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        logger.log("Temporary 'SOURCES', 'SPECS', 'SRPMS' directories created.", 1)

    def prepare(self) -> bool:
        """
        This method prepares all files necessary for source package assembly.

        This includes

        - copying every file (not directories) from package source directory to `rpmbuild/SOURCES`,
        - removing the latest tarball from the package source directory if it should not be kept,
        - copying the package configuration file to `rpmbuild/SOURCES`
        - preparing the `package.spec` file in `rpmbuild/SPECS` from the file in the spec directory,
        - defining macros for git and bzr version string additions,
        - setting `Version:` and `Release:` tags according to configuration,
        - appending a changelog entry automatically for every different build,
        - copying back the modified spec file to preserve added changelog entries.

        Arguments:
            bool relreset:  force release reset (triggered by major version or VCS update)
            bool force:     force release increment (triggered by packaging-only changes)

        Returns:
            bool:           returns `True` if the preparation was successful.
        """

        if not self.active:
            return False

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        if not os.path.exists(self.rpmbdir):
            warnings.warn("Make sure to call Constructor.init() before .prepare()!", Warning)
            self.init()

        # copy sources to rpmbuild/SOURCES
        for entry in os.listdir(self.cpkg.get_source().sdir):
            entry_path = os.path.join(self.cpkg.get_source().sdir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.srcsdir)
                logger.log("File copied to SOURCES: " + entry_path, 1)

        # remove tarballs if they should not be kept
        if not self.cpkg.conf.getboolean("source", "keep"):

            # if source is a tarball (or similar) from the beginning:
            if os.path.isfile(self.cpkg.get_source().dest):
                os.remove(self.cpkg.get_source().dest)

            # otherwise it is in kentauros' standard .tar.gz format:
            else:
                tarballs = glob.glob(os.path.join(self.cpkg.get_source().sdir,
                                                  self.cpkg.name) + "*.tar.gz")
                # remove only the newest one to be safe
                tarballs.sort(reverse=True)
                if os.path.isfile(tarballs[0]):
                    assert self.cpkg.get_source().sdir in tarballs[0]
                    os.remove(tarballs[0])
                    logger.log("Tarball removed: " + tarballs[0], 1)

        # copy package.conf to rpmbuild/SOURCES
        shutil.copy2(self.cpkg.file, self.srcsdir)
        logger.log("Package configuration copied to SOURCES: " + self.cpkg.file, 1)

        # construct preamble and new version string
        old_version = self._get_last_version(self.spec)
        new_version = self.cpkg.conf.get("source", "version")
        # old_release = self._get_last_release(self.spec)

        # TODO: check if release resetting / incrementing logic works now

        self.spec.set_version()

        # if old version and new version are different, force release reset to 0
        relreset = (new_version != old_version)

        # start constructing release string from old release string
        if relreset:
            self.spec.do_release_reset()

        # write preamble to new spec file
        preamble = self.spec.build_preamble_string()

        # calculate absolute path of new spec file and copy it over
        new_spec_path = os.path.join(self.specdir, self.cpkg.name + ".spec")
        self.spec.export_to_file(new_spec_path)

        # use "rpmdev-bumpspec" to increment release number and create changelog entries
        force = ktr.cli.get_force()

        logger.dbg("Old Version: " + old_version)
        logger.dbg("New Version: " + new_version)

        new_rpm_spec = RPMSpec(new_spec_path, self.cpkg.get_source())

        # if major version has changed, put it into the changelog
        if old_version != new_version:
            do_release_bump(new_spec_path,
                            "Update to version " + self.cpkg.conf.get("source", "version") + ".")
            # new_release = 1

        # else if nothing changed but "force" was set (packaging changes)
        # old_version =!= new_version, relreset !=!= True
        elif force:
            message = ktr.cli.get_message()
            if message is None:
                do_release_bump(new_spec_path, "Update for packaging changes.")
            else:
                do_release_bump(new_spec_path, message)

            # new_release = int(old_release) + 1

        # else if version has not changed, but snapshot has been updated:
        # old_version =!= new_version
        elif relreset:
            new_rpm_spec.do_release_reset()
            do_release_bump(new_spec_path, "Update to latest snapshot.")
            new_rpm_spec = RPMSpec(new_spec_path, self.cpkg.get_source())
            # new_release = 1

        else:
            return False

        # TODO: ktr.state_write(self.cpkg.conf_name, dict(rpm_last_release=str(new_release)))

        # copy new specfile back to ktr/specdir to preserve version tracking,
        # release number and changelog consistency (keep old version once as backup)
        # BUT: remove preamble again, it would break things otherwise

        new_rpm_spec.contents = new_rpm_spec.contents.replace(preamble, "")
        shutil.copy2(self.path, self.path + ".old")
        new_rpm_spec.export_to_file(self.path)

        return True

    def build(self):
        """
        This method executes the actual SRPM package assembly. It sets `$HOME` to the created
        temporary directory and executes `rpmbuild -bs` with the copy of the package spec file in
        `rpmbuild/SPECS`. After that, `$HOME` is reset to the old value.
        """

        if not self.active:
            return

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        old_home = os.environ['HOME']
        os.environ['HOME'] = self.tempdir

        # construct rpmbuild command
        cmd = ["rpmbuild"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        cmd.append("-bs")
        cmd.append(os.path.join(self.specdir, self.cpkg.name + ".spec"))

        logger.log_command(cmd)

        try:
            subprocess.call(cmd)
        finally:
            os.environ['HOME'] = old_home

    def export(self):
        """
        This method copies the assembled source packages from `rpmbuild/SRPMS`
        to the directory for built packages as specified in the kentauros
        configuration. If multiple SRPM packages are found, they all are copied.
        """

        if not self.active:
            return None

        logger = KtrLogger(LOGPREFIX)

        srpms = glob.glob(os.path.join(self.srpmdir, "*.src.rpm"))

        os.makedirs(self.pdir, exist_ok=True)

        for srpm in srpms:
            shutil.copy2(srpm, self.pdir)
            logger.log("File copied: " + srpm, 0)

    def clean(self):
        if not self.active:
            return None

        shutil.rmtree(self.tempdir)

# TODO: one uber-method for running everything in correct order
