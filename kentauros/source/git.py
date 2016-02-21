"""
kentauros.source.git
contains GitSource class and methods
this class is for handling sources that are specified by git repo URL
"""

import glob
import os
import shutil
import subprocess

from kentauros.init import DEBUG, VERBY, dbg, err, log
from kentauros.config import KTR_CONF
from kentauros.source.common import Source, SourceType


class GitSource(Source):
    """
    kentauros.source.GitSource
    information about and methods for git repositories available at specified URL
    this defaults to:
    - full checkout of source
    - keeping sources between transactions
    - checking out master branch
    """

    def __init__(self, pkgconfig):
        super().__init__(pkgconfig)
        self.config = pkgconfig
        self.daily = 0
        self.type = SourceType.GIT

        self.branch = pkgconfig['git']['branch']
        self.commit = pkgconfig['git']['commit']
        self.gitkeep = bool(pkgconfig['git']['keep'])
        self.shallow = bool(pkgconfig['git']['shallow'])

        # either branch or commit must be set. default to branch=master
        if self.branch == "" and self.commit == "":
            self.branch = "master"

        # shallow clones and checking out a specific commit is not supported
        if self.commit != "":
            self.shallow = False


    def date(self):
        """
        kentauros.source.git.date()
        returns date of HEAD commit
        """

        cmd = ["git", "show", "-s", "--date=short", "--format=%cd"]

        prevdir = os.getcwd()

        if not os.access(self.dest, os.R_OK):
            err("Sources need to be .get() before .date() can be determined.")
            return None

        os.chdir(self.dest)
        dbg("git command: " + str(cmd))
        date = subprocess.check_output(cmd).decode().rstrip('\r\n').replace("-", "")
        os.chdir(prevdir)

        return date


    def rev(self):
        """
        kentauros.source.git.rev()
        returns commit id of repository
        """

        cmd = ["git", "rev-parse", "HEAD"]

        prevdir = os.getcwd()

        if not os.access(self.dest, os.R_OK):
            err("Sources need to be .get() before .rev() can be determined.")
            return None

        os.chdir(self.dest)
        dbg("git command: " + str(cmd))
        rev = subprocess.check_output(cmd).decode().rstrip('\r\n')
        os.chdir(prevdir)

        return rev


    def formatver(self):
        ver = self.version          # base version
        ver += "~git"               # git prefix
        ver += self.date()          # date of commit
        ver += "."
        ver += str(self.daily)      # incr in case of multiple builds per day
        ver += "~"
        ver += self.rev()[0:8]      # first 8 chars of git commit ID
        return ver


    def get(self):
        """
        kentauros.source.git.get()
        get sources from specified branch at orig
        returns commit id of latest commit
        """

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, quit and return commit id
        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            log("Sources already downloaded. Latest commit id:", 1)
            log(rev, 1)
            return rev

        # construct git commands
        cmd = ["git"]

        # construct clone command
        cmd1 = cmd
        cmd1.append("clone")

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd1.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd1.append("--verbose")

        # set --depth==1 if shallow and no commit is specified
        if self.shallow and not self.commit:
            cmd1.append("--depth=1")

        # set branch if specified
        if self.branch:
            cmd1.append("--branch")
            cmd1.append(self.branch)

        # set origin and destination
        cmd1.append(self.orig)
        cmd1.append(self.dest)

        # clone git repo from orig to dest
        dbg("git command: " + str(cmd1))
        subprocess.call(cmd1)

        # if commit is specified: checkout commit
        if self.commit:
            # construct checkout command
            cmd2 = cmd
            cmd2.append("checkout")
            cmd2.append(self.commit)

            # go to git repo and remember old cwd
            prevdir = os.getcwd()
            os.chdir(self.dest)

            # checkout commit
            dbg("git command: " + str(cmd2))
            subprocess.call(cmd2)

            # go to previous dir
            os.chdir(prevdir)

        # get commit ID
        rev = self.rev()

        # check if checkout worked
        if self.commit:
            if self.commit != rev:
                err("Something went wrong, requested commit is not commit in repo.")

        # return commit ID
        return rev


    def update(self):
        """
        kentauros.source.git.update()
        update sources to latest commit in specified branch
        returns commit id of new commit, otherwise returns None
        """

        # construct git command
        cmd = ["git"]

        cmd.append("pull")
        cmd.append("--rebase")

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            err("Sources need to be .get() before .update() can be run.")
            return None

        # get old commit ID
        rev_old = self.rev()
        date_old = self.date()

        # change to git repodir
        prevdir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        dbg("git command: " + str(cmd))
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prevdir)

        # get new commit ID
        rev_new = self.rev()
        date_new = self.date()

        # return True if update found, False if not
        if rev_new != rev_old:
            # if new snapshot is of same day as old snapshot: verion incr
            if date_new == date_old:
                self.daily += 1
            # if new snapshot is of other day as old snapshot: verion reset
            else:
                self.daily = 0
            return True
        else:
            return False


    def refresh(self):
        self.clean()
        self.get()


    def export(self):
        """
        kentauros.source.git.export()
        exports current git commit to tarball (.tar.gz)
        """

        # construct git command
        cmd = ["git"]

        cmd.append("archive")

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.commit == "":
            cmd.append("HEAD")
        else:
            cmd.append(self.commit)

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            err("Sources need to be .get() before they can be .export()ed.")
            return None

        version = self.formatver()
        name_version = self.name + "-" + version

        # add prefix
        cmd.append("--prefix=" + name_version + "/")

        file_name = os.path.join(KTR_CONF['main']['datadir'],
                                 self.name,
                                 name_version + ".tar.gz")

        cmd.append("--output")
        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            log("Tarball has already been exported.", 1)
            return False

        # remember previous directory
        prevdir = os.getcwd()

        # change to git repodir
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        dbg("git command: " + str(cmd))
        subprocess.call(cmd)

        if not self.gitkeep:
            os.chdir(self.sdir)
            tarballs = glob.glob(self.name + "*.tar.gz")
            for tarball in tarballs:
                abspath = os.path.abspath(tarball)
                assert KTR_CONF['main']['datadir'] in abspath
                os.remove(abspath)

        os.chdir(prevdir)
        return True


    def clean(self):
        """
        kentauros.source.git.update()
        update sources to latest commit in specified branch
        returns commit id of new commit, otherwise returns None
        """

        if not os.access(self.dest, os.R_OK):
            log("Nothing here to be cleaned.", 0)

        else:
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert KTR_CONF['main']['datadir'] in self.dest
            shutil.rmtree(self.dest)

