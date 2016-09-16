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
from kentauros.construct.con_abstract import Constructor
from kentauros.pkgformat.rpm import RPMSpec


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

        ktr = Kentauros(LOGPREFIX)

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
            ktr.log("Install rpmdevtools to use the specified constructor.")
            self.active = False

    def init(self):
        """
        This method creates a temporary directory (which is then set to `$HOME` in the
        :py:meth:`SrpmConstructor.build()` method) and other necessary subdirectores (here:
        `SOURCES`, `SRPMS`, `SPECS`).
        """

        if not self.active:
            return

        ktr = Kentauros(LOGPREFIX)

        # make sure to finally call self.clean()!
        self.tempdir = tempfile.mkdtemp()

        ktr.log("Temporary directory " + self.tempdir + " created.", 1)

        self.rpmbdir = os.path.join(self.tempdir, "rpmbuild")
        self.specdir = os.path.join(self.tempdir, "rpmbuild", "SPECS")
        self.srpmdir = os.path.join(self.tempdir, "rpmbuild", "SRPMS")
        self.srcsdir = os.path.join(self.tempdir, "rpmbuild", "SOURCES")

        # create $TEMPDIR/rpmbuild
        if not os.path.exists(self.rpmbdir):
            os.mkdir(self.rpmbdir)

        ktr.log("Temporary rpmbuild directory created: " + self.tempdir, 1)

        # create $TEMPDIR/rpmbuild/{SPECS,SRPMS,SOURCES}
        for directory in [self.specdir, self.srpmdir, self.srcsdir]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        ktr.log("Temporary 'SOURCES', 'SPECS', 'SRPMS' directories created.", 1)

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

        ktr = Kentauros(LOGPREFIX)

        if not os.path.exists(self.rpmbdir):
            warnings.warn("Make sure to call Constructor.init() before .prepare()!", Warning)
            self.init()

        # calculate absolute paths of files
        pkg_conf_file = os.path.join(ktr.conf.get_confdir(), self.cpkg.conf_name + ".conf")
        pkg_spec_name = self.cpkg.name + ".spec"
        pkg_spec_file = os.path.join(ktr.conf.get_specdir(), self.cpkg.conf_name, pkg_spec_name)

        # copy sources to rpmbuild/SOURCES
        for entry in os.listdir(self.cpkg.source.sdir):
            entry_path = os.path.join(self.cpkg.source.sdir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.srcsdir)
                ktr.log("File copied: " + entry_path, 1)

        # remove tarballs if they should not be kept
        if not self.cpkg.conf.getboolean("source", "keep"):
            # if source is a tarball (or similar) from the beginning:
            if os.path.isfile(self.cpkg.source.dest):
                os.remove(self.cpkg.source.dest)

            # otherwise it is in kentauros' standard .tar.gz format:
            else:
                tarballs = glob.glob(os.path.join(self.cpkg.source.sdir,
                                                  self.cpkg.name) + "*.tar.gz")
                # remove only the newest one to be safe
                tarballs.sort(reverse=True)
                if os.path.isfile(tarballs[0]):
                    assert self.cpkg.source.sdir in tarballs[0]
                    os.remove(tarballs[0])
                    ktr.log("File removed: " + tarballs[0], 1)

        # copy package.conf to rpmbuild/SOURCES
        shutil.copy2(pkg_conf_file, self.srcsdir)
        ktr.log("File copied: " + pkg_conf_file, 1)

        # calculate absolute path of new spec file and copy it over
        new_spec_file = os.path.join(self.specdir, self.cpkg.name + ".spec")
        shutil.copy2(pkg_spec_file, new_spec_file)

        new_rpm_spec = RPMSpec(new_spec_file, self.cpkg.source)

        # construct preamble and new version string
        old_version = new_rpm_spec.read_version()
        new_version = new_rpm_spec.build_version_string()
        new_rpm_spec.write_version()

        # TODO: rework the release resetting / incrementing logic so it actually works
        # TODO: check if it works now

        # if old version and new version are different, force release reset to 0
        relreset = (new_version != old_version)

        # start constructing release string from old release string
        if relreset:
            new_rpm_spec.do_release_reset()

        # write preamble to new spec file
        new_rpm_spec.prepend_preamble()

        # use "rpmdev-bumpspec" to increment release number and create changelog entries
        force = ktr.cli.get_force()

        ktr.dbg("Old Version: " + old_version)
        ktr.dbg("New Version: " + new_version)

        # if major version has changed, put it into the changelog
        if old_version != new_version:
            new_rpm_spec.do_release_bump("Update to version " + str(new_version) + ".")

        # else if nothing changed but "force" was set (packaging changes)
        # old_version =!= new_version, relreset !=!= True
        elif force:
            message = ktr.cli.get_message()
            if message is None:
                new_rpm_spec.do_release_bump("Update for packaging changes.")
            else:
                new_rpm_spec.do_release_bump(message)

        # else if version has not changed, but snapshot has been updated:
        # old_version =!= new_version
        elif relreset:
            new_rpm_spec.do_release_reset()
            new_rpm_spec.do_release_bump("Update to latest snapshot.")

        # copy new specfile back to ktr/specdir to preserve version tracking,
        # release number and changelog consistency (keep old version once as backup)
        # BUT: remove preamble again, it would break things otherwise
        shutil.move(pkg_spec_file, pkg_spec_file + ".old")

        # write spec file without preamble back into place
        new_rpm_spec.path = pkg_spec_file
        new_rpm_spec.unprepend_preamble()

        return True

    def build(self):
        """
        This method executes the actual SRPM package assembly. It sets `$HOME` to the created
        temporary directory and executes `rpmbuild -bs` with the copy of the package spec file in
        `rpmbuild/SPECS`. After that, `$HOME` is reset to the old value.
        """

        if not self.active:
            return

        ktr = Kentauros(LOGPREFIX)

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

        ktr.log_command(cmd)

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

        ktr = Kentauros(LOGPREFIX)

        srpms = glob.glob(os.path.join(self.srpmdir, "*.src.rpm"))

        packdir = os.path.join(ktr.conf.get_packdir(), self.cpkg.conf_name)

        os.makedirs(packdir, exist_ok=True)

        for srpm in srpms:
            shutil.copy2(srpm, packdir)
            ktr.log("File copied: " + srpm, 0)

    def clean(self):
        if not self.active:
            return None

        shutil.rmtree(self.tempdir)

# TODO: one uber-method for running everything in correct order
