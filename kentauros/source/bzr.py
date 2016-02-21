"""
kentauros.source.bzr
contains GitSource class and methods
this class is for handling sources that are specified by bzr repo URL
"""

from kentauros.source.common import Source, SourceType


class BzrSource(Source):
    """
    kentauros.source.BzrSource
    information about and methods for bzr repositories available at specified URL
    """
    def __init__(self):
        super().__init__()
        self.type = SourceType.BZR

    def get(self):
        # TODO: download bzr repo from orig to dest (package name?)
        # is shallow possible with bzr?
        pass

    def update(self):
        # TODO: bzr pull in source repo
        pass

    def refresh(self):
        # TODO: remove source repo ad exported tarballs from datadir
        # and redownload bzr repo
        pass

    def export(self):
        # TODO: bzr archive tar.gz to datadir
        pass

    def clean(self):
        # TODO: remove downloaded bzr repo and exported files
        # from datadir (respect keep, force)
        pass

