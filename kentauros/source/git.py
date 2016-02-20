"""
kentauros.source.git
contains GitSource class and methods
this class is for handling sources that are specified by git repo URL
"""

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

        self.branch = pkgconfig['git']['branch']
        self.commit = pkgconfig['git']['commit']
        self.gitkeep = bool(pkgconfig['git']['keep'])
        self.shallow = bool(pkgconfig['git']['shallow'])
        self.type = SourceType.GIT


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
        return self.version + "~git" + self.date() + "~" + self.rev()[0:8]


    def get(self):
        """
        kentauros.source.git.get()
        get sources from specified branch at orig
        returns commit id of latest commit
        """

        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            log("Sources already downloaded. Latest commit id:", 1)
            log(rev, 1)
            return rev

        cmd = ["git", "clone"]

        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        if self.shallow:
            cmd.append("--depth=1")

        cmd.append("--branch")
        cmd.append(self.branch)

        # TODO: check out commit instead if branch master if specified

        cmd.append(self.orig)
        cmd.append(self.dest)

        dbg("git command: " + str(cmd))
        subprocess.call(cmd)

        rev = self.rev()
        return rev


    def update(self):
        """
        kentauros.source.git.update()
        update sources to latest commit in specified branch
        returns commit id of new commit, otherwise returns None
        """

        cmd = ["git", "pull", "--rebase"]

        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        prevdir = os.getcwd()

        if not os.access(self.dest, os.R_OK):
            err("Sources need to be .get() before .update() can be run.")
            return None

        rev_old = self.rev()

        os.chdir(self.dest)
        dbg("git command: " + str(cmd))
        subprocess.call(cmd)
        os.chdir(prevdir)

        rev_new = self.rev()

        if rev_new != rev_old:
            return True
        else:
            return False


    def refresh(self):
        self.clean()
        self.get()

    """
    def export(self):
        # TODO: git archive HEAD > tar.gz to datadir
        ""
        kentauros.source.git.export()
        exports current git commit to tarball (.tar.gz)
        ""

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
    """

    def clean(self):
        """
        kentauros.source.git.update()
        update sources to latest commit in specified branch
        returns commit id of new commit, otherwise returns None
        """

        if not os.access(self.dest, os.R_OK):
            log("Nothing here to be cleaned.", 0)
            return False

        # try to be careful with "rm -r"
        assert os.path.isabs(self.dest)
        assert KTR_CONF['main']['datadir'] in self.dest
        shutil.rmtree(self.dest)

