"""
kentauros.construct module
contains classes, methods and functions for building source packages
"""

import glob
import os
import shutil
import subprocess
import tempfile

from kentauros.config import KTR_CONF
from kentauros.construct.rpm_spec import munge_line, spec_bump
from kentauros.definitions import SourceType
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


    def init(self):
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

        log(LOGPREFIX1 + "Temporary SOURCES, SPECS, SRPMS directory created.", 1)


    def prepare(self, relreset=False):
        if not os.path.exists(self.rpmbdir):
            self.init()

        pkg_data_dir = os.path.join(KTR_CONF.get("main", "datadir"),
                                    self.package.name)

        pkg_conf_file = os.path.join(KTR_CONF.get("main", "confdir"),
                                     self.package.name + ".conf")

        pkg_spec_file = os.path.join(KTR_CONF.get("main", "specdir"),
                                     self.package.name + ".spec")

        for entry in os.listdir(pkg_data_dir):
            entry_path = os.path.join(pkg_data_dir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.srcsdir)
                log(LOGPREFIX1 + "File copied: " + entry_path, 0)

        shutil.copy2(pkg_conf_file, self.srcsdir)
        log(LOGPREFIX1 + "File copied: " + pkg_conf_file, 0)

        new_spec_file = os.path.join(self.specdir, self.package.name + ".spec")

        old_specfile = open(pkg_spec_file, "r")
        new_specfile = open(new_spec_file, "x")

        # TODO: use dict of functions for different enum members of SourceType (bzr, git)
        if self.package.source.type == SourceType.GIT:
            date_define = "%define date " + \
                          self.package.source.date() + "\n"
            rev_define = "%define rev " + \
                         self.package.source.rev()[0:8] + "\n"

            new_specfile.write(date_define)
            new_specfile.write(rev_define)
            new_specfile.write("\n")

        if self.package.source.type == SourceType.BZR:
            rev_define = "%define rev " + self.package.source.rev() + "\n"
            new_specfile.write(rev_define)
            new_specfile.write("\n")

        for line in old_specfile:
            new_specfile.write(munge_line(line, self.package, relreset=relreset))

        old_specfile.close()
        new_specfile.close()

        spec_bump(new_spec_file)


    def build(self):
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
        srpms = glob.glob(os.path.join(self.srpmdir, "*.src.rpm"))

        for srpm in srpms:
            shutil.copy2(srpm, KTR_CONF.get("main", "packdir"))
            log(LOGPREFIX1 + "File copied: " + srpm, 0)


    def clean(self):
        shutil.rmtree(self.tempdir)

