"""
This module contains the :py:class:`SrpmConstructor` class, which can be used
to construct src.rpm packages.
"""


import glob
import os
import shutil
import subprocess
import tempfile

from kentauros.instance import Kentauros, log, log_command

from kentauros.construct.constructor import Constructor

from kentauros.construct.rpm_spec import SPEC_PREAMBLE_DICT, SPEC_VERSION_DICT
from kentauros.construct.rpm_spec import RPMSpecError
from kentauros.construct.rpm_spec import spec_version_read, spec_release_read
from kentauros.construct.rpm_spec import if_version, if_release, format_tagline
from kentauros.construct.rpm_spec import reset_release, spec_bump


LOGPREFIX1 = "ktr/construct/srpm: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class SrpmConstructor(Constructor):
    """
    This :py:class:`Constructor` subclass implements methods for all stages of
    building and exporting source packages. At class instantiation, it checks
    for existance of ``rpmbuild`` and ``rpmdev-bumpspec`` binaries. If they are
    not found in ``$PATH``, this instance is set to inactive.

    Arguments:
        Package package: package for which this src.rpm constructor is for

    Attributes:
        bool active: determines if this instance is active
        str tempdir: absolute path of temporary "HOME" directory
        str rpmbdir: absolute path of ``rpmbuild`` directory
        str specdir: absolute path of ``rpmbuild/SPECS`` directory
        str srpmdir: absolute path of ``rpmbuild/SRPMS`` directory
        str srcsdir: absolute path of ``rpmbuild/SOURCES`` directory
    """

    def __init__(self, package):
        super().__init__(package)

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
            log(LOGPREFIX1 + \
                "Install rpmdevtools to use the specified constructor.")
            self.active = False


    def init(self):
        """
        This method creates a temporary directory (which is then set to `$HOME`
        in the :py:meth:`SrpmConstructor.build()` method) and other necessary
        subdirectores (here: `SOURCES`, `SRPMS`, `SPECS`).
        """

        if not self.active:
            return

        # make sure to finally call self.clean()!
        self.tempdir = tempfile.mkdtemp()

        log(LOGPREFIX1 + "Temporary directory " + self.tempdir + " created.", 1)

        self.rpmbdir = os.path.join(self.tempdir, "rpmbuild")
        self.specdir = os.path.join(self.tempdir, "rpmbuild", "SPECS")
        self.srpmdir = os.path.join(self.tempdir, "rpmbuild", "SRPMS")
        self.srcsdir = os.path.join(self.tempdir, "rpmbuild", "SOURCES")

        # create $TEMPDIR/rpmbuild
        if not os.path.exists(self.rpmbdir):
            os.mkdir(self.rpmbdir)

        log(LOGPREFIX1 + "Temporary rpmbuild directory created:", 1)
        log(LOGPREFIX1 + self.tempdir, 1)

        # create $TEMPDIR/rpmbuild/{SPECS,SRPMS,SOURCES}
        for directory in [self.specdir, self.srpmdir, self.srcsdir]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        log(LOGPREFIX1 + \
            "Temporary 'SOURCES', 'SPECS', 'SRPMS' directories created.", 1)


    def prepare(self, relreset: bool=False, force: bool=False) -> bool:
        """
        This method prepares all files necessary for source package assembly.

        This includes

        - copying every file (not directories) from package source directory to
          `rpmbuild/SOURCES` directory,
        - removing the latest tarball from the package source directory if it
          should not be kept,
        - copying the package configuration file to `rpmbuild/SOURCES` in case
          it will be included in the source package
        - preparing the `package.spec` file in `rpmbuild/SPECS` from the
          template in the spec directory,
        - defining macros for git and bzr version string additions,
        - setting `Version:` and `Release:` tags according to configuration,
        - appending a changelog entry automatically for every different build,
        - copying back the modified spec file (sans macros) to preserve newly
          added changelog entries.

        Arguments:
            bool relreset:  force version reset (triggered e. g. by CVS update)

        Returns:
            bool:           returns `True` if the preparation was successful.
        """

        if not self.active:
            return False

        ktr = Kentauros()

        if not os.path.exists(self.rpmbdir):
            self.init()

        # calculate absolute paths of files
        pkg_data_dir = os.path.join(ktr.conf.datadir, self.pkg.name)
        pkg_conf_file = os.path.join(ktr.conf.confdir, self.pkg.name + ".conf")
        pkg_spec_file = os.path.join(ktr.conf.specdir, self.pkg.name + ".spec")

        # copy sources to rpmbuild/SOURCES
        for entry in os.listdir(pkg_data_dir):
            entry_path = os.path.join(pkg_data_dir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.srcsdir)
                log(LOGPREFIX1 + "File copied: " + entry_path, 0)

        # remove tarballs if they should not be kept
        if not self.pkg.conf.getboolean("source", "keep"):
            # remove $DATADIR/$PKGNAME/$PKGNAME*.tar.gz
            tarballs = glob.glob(
                os.path.join(pkg_data_dir, self.pkg.name) + "*.tar.gz")
            # remove only the newest one to be safe
            tarballs.sort(reverse=True)
            if os.path.isfile(tarballs[0]):
                assert pkg_data_dir in tarballs[0]
                os.remove(tarballs[0])
                log(LOGPREFIX1 + "File removed: " + tarballs[0], 0)

        # copy package.conf to rpmbuild/SOURCES
        shutil.copy2(pkg_conf_file, self.srcsdir)
        log(LOGPREFIX1 + "File copied: " + pkg_conf_file, 0)

        # calculate absolute path of new spec file
        new_spec_file = os.path.join(self.specdir, self.pkg.name + ".spec")

        # open old and create new spec file
        old_specfile = open(pkg_spec_file, "r")
        new_specfile = open(new_spec_file, "x")

        # try to read old Version string from old specfile (resets seek=0)
        try:
            old_version = spec_version_read(old_specfile)
        except RPMSpecError:
            log(LOGPREFIX1 + \
                "RPM spec file not valid. Version tag line not found.", 2)
            old_specfile.close()
            new_specfile.close()
            return False

        # try to read old Release string from old specfile (resets seek=0)
        try:
            old_release = spec_release_read(old_specfile)
        except RPMSpecError:
            log(LOGPREFIX1 + \
                "RPM spec file not valid. Release tag line not found.", 2)
            old_specfile.close()
            new_specfile.close()
            return False

        # construct preamble and new version string
        preamble = SPEC_PREAMBLE_DICT[self.pkg.source.type](self.pkg.source)
        new_version = SPEC_VERSION_DICT[self.pkg.source.type](self.pkg.source)

        # if old version and new version are different, force release reset to 0
        if new_version != old_version:
            relreset = True

        # construct new release string
        if relreset:
            new_release = reset_release(old_release)

        # write preamble to new spec file
        new_specfile.write(preamble)

        # write rest of file and change Version and Release tags accordingly
        for line in old_specfile:
            if if_version(line):
                new_specfile.write(format_tagline("Version", new_version))
            elif if_release(line):
                new_specfile.write(format_tagline("Release", new_release))
            else:
                new_specfile.write(line)

        # close files
        old_specfile.close()
        new_specfile.close()

        # use "rpmdev-bumpspec" to increment release number and create
        # changelog entries

        # if major version has changed, put it into the changelog
        if old_version != new_version:
            spec_bump(new_spec_file, comment="Update to version " +
                      self.pkg.conf.get("source", "version") + ".")

        # else if version has not changed, but snapshot has been updated:
        # old_version =!= new_version
        elif relreset:
            spec_bump(new_spec_file, comment="Update to latest snapshot.")

        # else if nothing changed but "force" was set (packaging changes)
        # old_version =!= new_version, relreset !=!= True
        elif force:
            spec_bump(new_spec_file, comment="Update for packaging changes.")

        # copy new specfile back to ktr/specdir to preserve version tracking,
        # release number and changelog consistency (keep old version once as
        # backup)
        # BUT: remove preamble again, it would break things otherwise
        shutil.move(pkg_spec_file, pkg_spec_file + ".old")

        # open new and create old spec file
        old_specfile = open(new_spec_file, "r")
        new_specfile = open(pkg_spec_file, "x")

        # read all text from new spec in one go
        spec_text = old_specfile.read()

        # replace preamble with nothing
        spec_text = spec_text.replace(preamble, "", 1)

        # write everything but the preamble to "old" spec location
        new_specfile.write(spec_text)

        # close files
        old_specfile.close()
        new_specfile.close()

        return True


    def build(self):
        """
        This method executes the actual SRPM package assembly. It sets `$HOME`
        to the created temporary directory and executes `rpmbuild -bs` with the
        copy of the package spec file in `rpmbuild/SPECS`. After that, `$HOME`
        is reset to the old value.
        """

        if not self.active:
            return

        ktr = Kentauros()

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

        cmd.append(os.path.join(self.specdir, self.pkg.name + ".spec"))

        log_command(LOGPREFIX1, "rpmbuild", cmd, 1)
        subprocess.call(cmd)

        os.environ['HOME'] = old_home


    def export(self):
        """
        This method copies the assembled source packages from `rpmbuild/SRPMS`
        to the directory for built packages as specified in the kentauros
        configuration. If multiple SRPM packages are found, they all are copied.
        """

        if not self.active:
            return None

        srpms = glob.glob(os.path.join(self.srpmdir, "*.src.rpm"))

        for srpm in srpms:
            shutil.copy2(srpm, Kentauros().conf.packdir)
            log(LOGPREFIX1 + "File copied: " + srpm, 0)


    def clean(self):
        if not self.active:
            return None

        shutil.rmtree(self.tempdir)

