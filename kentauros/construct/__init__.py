"""
kentauros.construct module
contains classes, methods and functions for building source packages
"""

import glob
import os
import shutil
import subprocess
import tempfile

from kentauros.config import ktr_get_conf

from kentauros.construct.rpm_spec import SPEC_PREAMBLE_DICT, SPEC_VERSION_DICT
from kentauros.construct.rpm_spec import RPMSpecError
from kentauros.construct.rpm_spec import spec_version_read, spec_release_read
from kentauros.construct.rpm_spec import if_version, if_release
from kentauros.construct.rpm_spec import bump_release, spec_bump

from kentauros.definitions import SourceType, ConstructorType
from kentauros.init import VERBY, DEBUG, log, log_command


LOGPREFIX1 = "ktr/construct: "


class Constructor:
    """
    kentauros.construct.Constructor:
    base class for source package preparators
    """
    def __init__(self, package):
        self.package = package

    def init(self):
        """
        kentauros.construct.Constructor.init()
        method that creates directories needed for source package building
        """
        pass

    def prepare(self, relreset=False):
        """
        kentauros.construct.Constructor.prepare()
        method that copies files needed for source package building
        """
        pass

    def build(self):
        """
        kentauros.construct.Constructor.build()
        method that builds source package
        """
        pass

    def export(self):
        """
        kentauros.construct.Constructor.export()
        method that moves built source package
        """
        pass

    def clean(self):
        """
        kentauros.construct.Constructor.clean()
        method that cleans up temporary files
        """
        pass


class SrpmConstructor(Constructor):
    """
    kentauros.construct.SrpmConstructor:
    class for .src.rpm source package preparator
    """
    def __init__(self, package):
        super().__init__(package)

        self.tempdir = None
        self.rpmbdir = None
        self.specdir = None
        self.srpmdir = None
        self.srcsdir = None

        # if bzr is not installed: mark BzrSource instance as inactive
        try:
            self.active = True
            subprocess.check_output(["which", "rpmbuild"])
            subprocess.check_output(["which", "rpmdev-bumpspec"])
        except subprocess.CalledProcessError:
            log(LOGPREFIX1 + \
                "Install rpmdevtools to use the specified constructor.")
            self.active = False


    def init(self):
        if not self.active:
            return None

        # make sure to finally call self.clean()
        self.tempdir = tempfile.mkdtemp()

        log(LOGPREFIX1 + "Temporary directory " + self.tempdir + " created.", 1)

        self.rpmbdir = os.path.join(self.tempdir, "rpmbuild")
        self.specdir = os.path.join(self.tempdir, "rpmbuild", "SPECS")
        self.srpmdir = os.path.join(self.tempdir, "rpmbuild", "SRPMS")
        self.srcsdir = os.path.join(self.tempdir, "rpmbuild", "SOURCES")

        if not os.path.exists(self.rpmbdir):
            os.mkdir(self.rpmbdir)

        log(LOGPREFIX1 + "Temporary rpmbuild directory created.", 1)

        for directory in [self.specdir, self.srpmdir, self.srcsdir]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        log(LOGPREFIX1 + \
            "Temporary SOURCES, SPECS, SRPMS directory created.", 1)


    def prepare(self, relreset=False):
        if not self.active:
            return False

        if not os.path.exists(self.rpmbdir):
            self.init()

        ktr_conf = ktr_get_conf()

        # calculate absolute paths of files
        pkg_data_dir = os.path.join(ktr_conf.datadir,
                                    self.package.name)
        pkg_conf_file = os.path.join(ktr_conf.confdir,
                                     self.package.name + ".conf")
        pkg_spec_file = os.path.join(ktr_conf.specdir,
                                     self.package.name + ".spec")

        # copy sources to rpmbuild/SOURCES
        for entry in os.listdir(pkg_data_dir):
            entry_path = os.path.join(pkg_data_dir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.srcsdir)
                log(LOGPREFIX1 + "File copied: " + entry_path, 0)

        # copy package.conf to rpmbuild/SOURCES
        shutil.copy2(pkg_conf_file, self.srcsdir)
        log(LOGPREFIX1 + "File copied: " + pkg_conf_file, 0)

        # calculate absolute path of new spec file
        new_spec_file = os.path.join(self.specdir, self.package.name + ".spec")

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
        preamble = SPEC_PREAMBLE_DICT[self.package.source.type](
            self.package.source)
        new_version = SPEC_VERSION_DICT[self.package.source.type](
            self.package.source)

        # if old version and new version are different, force release reset to 0
        if new_version != old_version:
            relreset = True

        # construct new release string
        new_release = bump_release(old_release, relreset)

        # write preamble to new spec file
        new_specfile.write(preamble)

        # write rest of file and change Version and Release tags accordingly
        for line in old_specfile:
            if if_version(line):
                new_specfile.write("Version:" + 8 * " " + new_version + "\n")
            elif if_release(line):
                new_specfile.write("Release:" + 8 * " " + new_release + "\n")
            else:
                new_specfile.write(line)

        # close files
        old_specfile.close()
        new_specfile.close()

        # if version has changed, put it into the changelog
        if new_version != old_version:
            spec_bump(new_spec_file,
                      comment="update to version " + \
                              self.package.conf.get("source", "version"))
        else:
            spec_bump(new_spec_file)

        # copy new specfile back to ktr/specdir to preserve version tracking,
        # release number and changelog consistency (keep old version once as
        # backup) # BUT: remove preamble again, it would break things otherwise
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
        if not self.active:
            return None

        old_home = os.environ['HOME']
        os.environ['HOME'] = self.tempdir

        # construct rpmbuild command
        cmd = ["rpmbuild"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        cmd.append("-bs")

        cmd.append(os.path.join(self.specdir, self.package.name + ".spec"))

        log_command(LOGPREFIX1, "rpmbuild", cmd, 1)
        subprocess.call(cmd)

        os.environ['HOME'] = old_home


    def export(self):
        if not self.active:
            return None

        srpms = glob.glob(os.path.join(self.srpmdir, "*.src.rpm"))

        for srpm in srpms:
            shutil.copy2(srpm, ktr_get_conf().packdir)
            log(LOGPREFIX1 + "File copied: " + srpm, 0)


    def clean(self):
        if not self.active:
            return None

        shutil.rmtree(self.tempdir)


CONSTRUCTOR_TYPE_DICT = dict()
CONSTRUCTOR_TYPE_DICT[ConstructorType.NONE] = Constructor
CONSTRUCTOR_TYPE_DICT[ConstructorType.SRPM] = SrpmConstructor

