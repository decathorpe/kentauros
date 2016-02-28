"""
kentauros.source.bzr
contains GitSource class and methods
this class is for handling sources that are specified by bzr repo URL
"""

from distutils.util import strtobool
import os
import shutil
import subprocess

from kentauros.config import KTR_CONF
from kentauros.definitions import SourceType
from kentauros.init import DEBUG, VERBY, err, log, log_command
from kentauros.source.common import Source


LOGPREFIX1 = "ktr/source/bzr: "


class BzrSource(Source):
    """
    kentauros.source.bzr.BzrSource
    information about and methods for bzr repositories available at specified URL
    """
    def __init__(self, pkgconfig):
        super().__init__(pkgconfig)
        self.config = pkgconfig
        self.dest = os.path.join(self.sdir, self.name)
        self.type = SourceType.BZR


    def get_branch(self):
        """
        kentauros.source.bzr.BzrSource.get_branch():
        get from config which branch should be used
        """
        return self.conf['bzr']['branch']


    def get_bzrkeep(self):
        """
        kentauros.source.bzr.BzrSource.get_bzrkeep():
        get value from config if bzr repo should be kept after export to tarball
        """
        return bool(strtobool(self.conf['bzr']['keep']))


    def set_bzrkeep(self, keep):
        """
        kentauros.source.bzr.BzrSource.set_bzrkeep():
        set config value that determines whether bzr repo is kept after export to tarball
        """
        assert isinstance(keep, bool)
        self.conf['bzr']['keep'] = str(keep)


    def get_rev(self):
        """
        kentauros.source.bzr.BzrSource.get_rev():
        get value from config if bzr repo should be kept after export to tarball
        """
        return self.conf['bzr']['rev']


    def rev(self):
        """
        kentauros.source.bzr.BzrSource.rev()
        returns revision of repository as string
        """

        cmd = ["bzr", "revno"]

        prevdir = os.getcwd()

        if not os.access(self.dest, os.R_OK):
            err("Sources need to be .get() before .rev() can be determined.")
            return None

        os.chdir(self.dest)
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")
        os.chdir(prevdir)

        return rev


    def formatver(self):
        ver = self.get_version()    # base version
        ver += "~rev"               # bzr prefix
        ver += self.rev()           # revision number as string
        return ver


    def get(self):
        """
        kentauros.source.bzr.BzrSource.get()
        get sources from specified branch at orig
        returns revision number of latest commit
        """

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, quit and return revision number
        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            log(LOGPREFIX1 + "Sources already downloaded. Latest commit id:", 1)
            log(LOGPREFIX1 + rev, 1)
            return rev

        # construct bzr command
        cmd = ["bzr", "branch"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # set origin
        if not self.get_branch():
            cmd.append(self.get_orig())
        else:
            cmd.append(self.get_orig() + "/" + self.get_branch())

        # set revision is specified
        if self.get_rev():
            cmd.append("--revision")
            cmd.append(self.get_rev())

        # set destination
        cmd.append(self.dest)

        # branch bzr repo from orig to dest
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        subprocess.call(cmd)

        # get commit ID
        rev = self.rev()

        # check if checkout worked
        if self.get_rev():
            if self.get_rev() != rev:
                err(LOGPREFIX1 + "Something went wrong, requested commit is not commit in repo.")

        # return commit ID
        return rev


    def update(self):
        """
        kentauros.source.bzr.BzrSource.update()
        update sources to latest commit in specified branch
        returns True if update happened, False if not
        """

        # if specific revision is requested, do not pull updates (obviously)
        if self.get_rev():
            return False

        # construct bzr command
        cmd = ["bzr", "pull"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            err(LOGPREFIX1 + "Sources need to be .get() before .update() can be run.")
            return None

        # get old commit ID
        rev_old = self.rev()

        # change to git repodir
        prevdir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prevdir)

        # get new commit ID
        rev_new = self.rev()

        # return True if update found, False if not
        if rev_new != rev_old:
            return True
        else:
            return False


    def export(self):
        """
        kentauros.source.bzr.BzrSource.export()
        exports current bzr revision to tarball (.tar.gz)
        """

        # construct bzr command
        cmd = ["bzr", "export"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.get_rev():
            cmd.append("--revision")
            cmd.append(self.get_rev())

        # check if bzr repo exists
        if not os.access(self.dest, os.R_OK):
            err(LOGPREFIX1 + "Sources need to be .get() before they can be .export()ed.")
            return None

        version = self.formatver()
        name_version = self.name + "-" + version

        file_name = os.path.join(KTR_CONF['main']['datadir'],
                                 self.name,
                                 name_version + ".tar.gz")

        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            log(LOGPREFIX1 + "Tarball has already been exported.", 1)
            return False

        # remember previous directory
        prevdir = os.getcwd()

        # change to git repodir
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        subprocess.call(cmd)

        # remove bzr repo if keep is False
        print(self.get_bzrkeep())
        if not self.get_bzrkeep():
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert KTR_CONF['main']['datadir'] in self.dest
            shutil.rmtree(self.dest)
            log(LOGPREFIX1 + "bzr repo deleted after export to tarball", 1)

        os.chdir(prevdir)
        return True


    def clean(self):
        if not os.access(self.sdir, os.R_OK):
            log(LOGPREFIX1 + "Nothing here to be cleaned.", 0)
        else:
            # try to be careful with "rm -r"
            assert os.path.isabs(self.sdir)
            assert KTR_CONF['main']['datadir'] in self.sdir
            shutil.rmtree(self.sdir)

