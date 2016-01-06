"""
"""

import os
import subprocess

from kentauros.source.common import Source, SourceType


class GitSource(Source):
    """
    kentauros.source.GitSource
    information about and methods for git repositories available at specified URL
    """
    def __init__(self, keep=True, shallow=False):
        super().__init__()
        self.type = SourceType.GIT
        self.keep = keep
        self.shallow = shallow

    def get(self):
        # TODO: download git repo from orig to dest (package name?)
        # --depth=1 if shallow
        # returns revision of master
        cmd = ["git", "clone", orig, ]
        if not os.access(self.dir, os.W_OK):
            os.makedirs(self.dir)
        success = subprocess.call(["git", "clone", orig, os.path.join(self.dir, dest)])

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

