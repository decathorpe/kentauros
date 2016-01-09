"""
kentauros.source.git
contains GitSource class and methods
this class is for handling sources that are specified by git repo URL
"""

import os
import subprocess

from kentauros.init import DEBUG, VERBY, err, log
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

    def __init__(self,
                 name,
                 branch="master",
                 commit=None,
                 keep=True,
                 shallow=False):

        super().__init__(name)

        self.branch = branch
        self.commit = commit
        self.keep = keep
        self.lastdate = None
        self.lastrev = None
        self.shallow = shallow
        self.type = SourceType.GIT


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
        rev = subprocess.check_output(cmd).decode().rstrip('\r\n')
        os.chdir(prevdir)

        return rev


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

        cmd.append(self.orig)
        cmd.append(self.dest)

        log("git command: " + str(cmd), 0)
        subprocess.call(cmd)

        rev = self.rev()
        return rev


    def update(self, oldver=None, newver=None):
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
        log("git command: " + str(cmd), 0)
        subprocess.call(cmd)
        os.chdir(prevdir)

        rev_new = self.rev()

        if rev_new != rev_old:
            return rev_new
        else:
            return None


    def refresh(self):
        # TODO: remove source repo ad exported tarballs from datadir
        # and redownload git repo
        pass


    def export(self):
        # TODO: git archive HEAD > tar.gz to datadir
        pass


    def clean(self, force=False):
        # TODO: remove downloaded git repo from datadir (respect keep, force)
        pass

