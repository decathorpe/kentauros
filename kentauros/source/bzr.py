"""
"""

# import subprocess

from kentauros.source.common import Source, SourceType


class BzrSource(Source):
    """
    kentauros.source.BzrSource
    information about and methods for bzr repositories available at specified URL
    """
    def __init__(self, keep=True, shallow=False):
        super().__init__()
        self.type = SourceType.BZR
        self.keep = keep
        self.shallow = shallow

    def get(self):
        # TODO: download bzr repo from orig to dest (package name?)
        # is shallow possible with bzr?
        pass

    def update(self, oldver=None, newver=None):
        # TODO: bzr pull in source repo
        pass

    def refresh(self):
        # TODO: remove source repo ad exported tarballs from datadir
        # and redownload bzr repo
        pass

    def export(self):
        # TODO: bzr archive tar.gz to datadir
        pass

    def clean(self, force=False):
        # TODO: remove downloaded bzr repo and exported files
        # from datadir (respect keep, force)
        pass

