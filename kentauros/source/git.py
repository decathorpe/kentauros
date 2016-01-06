"""
kentauros.source.git
contains GitSource class and methods
this class is for handling sources that are specified by git repo URL
"""

import os
import subprocess

from kentauros.source.common import Source, SourceType


class GitSource(Source):
    """
    kentauros.source.GitSource
    information about and methods for git repositories available at specified URL
    """
    def __init__(self, name, keep=True, shallow=False):
        super().__init__(name)
        self.type = SourceType.GIT
        self.keep = keep
        self.shallow = shallow

    def get(self):
        # TODO: download git repo from orig to dest (package name?)
        # --depth=1 if shallow
        # returns revision of master
        cmd = ["git", "clone", self.orig, self.dest]
        cmd_shallow = ["git", "clone", "--depth=1", self.orig, self.dest]
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        if self.shallow:
            subprocess.call(cmd_shallow)
        else:
            subprocess.call(cmd)

    def update(self, oldver=None, newver=None):
        # TODO: git pull --rebase in source repo
        pass

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

