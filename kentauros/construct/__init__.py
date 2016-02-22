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
from kentauros.init import VERBY, DEBUG, log
from kentauros.source.common import SourceType


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

    def prepare(self):
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

        self.tempdir = tempfile.mkdtemp()

        log("construct: Temporary directory " + self.tempdir + " created.", 1)

        self.rpmbdir = os.path.join(self.tempdir, "rpmbuild")
        self.specdir = os.path.join(self.tempdir, "rpmbuild", "SPECS")
        self.srpmdir = os.path.join(self.tempdir, "rpmbuild", "SRPMS")
        self.srcsdir = os.path.join(self.tempdir, "rpmbuild", "SOURCES")


    def init(self):
        if not os.path.exists(self.rpmbdir):
            os.mkdir(self.rpmbdir)

        log("construct: Temporary rpmbuild directory created.", 1)

        for directory in [self.specdir, self.srpmdir, self.srcsdir]:
            if not os.path.exists(directory):
                os.mkdir(directory)

        log("construct: Temporary SOURCES, SPECS, SRPMS directory created.", 1)


    def prepare(self):
        if not os.path.exists(self.rpmbdir):
            self.init()

        pkg_data_dir = os.path.join(KTR_CONF['main']['datadir'],
                                    self.package.name)

        pkg_conf_file = os.path.join(KTR_CONF['main']['confdir'],
                                     self.package.name + ".conf")

        pkg_spec_file = os.path.join(KTR_CONF['main']['specdir'],
                                     self.package.name + ".spec")

        for entry in os.listdir(pkg_data_dir):
            entry_path = os.path.join(pkg_data_dir, entry)
            if os.path.isfile(entry_path):
                shutil.copy2(entry_path, self.srcsdir)
                log("construct: File copied: " + entry_path, 0)

        shutil.copy2(pkg_conf_file, self.srcsdir)
        log("construct: File copied: " + pkg_conf_file, 0)

        shutil.copy2(pkg_spec_file, self.specdir)
        log("construct: File copied: " + pkg_spec_file, 0)


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

        if self.package.source.type == SourceType.GIT:
            # define date macro
            cmd.append("--define=date " + \
                       self.package.source.date() + "." + \
                       str(self.package.source.daily))

            # define rev macro
            cmd.append("--define=rev " + \
                       self.package.source.rev()[0:8])

        # TODO: case bzr
        # TODO: case url

        pkg_spec_file = os.path.join(self.specdir, self.package.name + ".spec")

        cmd.append(pkg_spec_file)

        log("rpmbuild command: " + str(cmd), 1)
        subprocess.call(cmd)

        os.environ['HOME'] = old_home


    def export(self):
        srpms = glob.glob(os.path.join(self.srpmdir, "*.src.rpm"))

        for srpm in srpms:
            shutil.copy2(srpm, KTR_CONF['main']['packdir'])
            log("construct: File copied: " + srpm, 0)


    def clean(self):
        shutil.rmtree(self.tempdir)

