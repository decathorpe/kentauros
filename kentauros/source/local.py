"""
kentauros.source.local
contains LocalSource class and methods
this class is for handling sources that are specified by file path pointing to a tarball
"""

from kentauros.definitions import SourceType
from kentauros.source.common import Source


class LocalSource(Source):
    """
    kentauros.source.LocalSource
    information about and methods for locally available source tarballs
    """
    def __init__(self, package):
        super().__init__(package)
        self.type = SourceType.LOCAL
        self.keep = True

    def get(self):
        # TODO: copy source from orig to datadir
        # don't do anything if orig is inside datadir
        pass

    def update(self):
        # local tarball does not need updating
        pass

    def refresh(self):
        # TODO: delete and re-copy source from orig to datadir
        # don't do anything if orig is inside datadir
        pass

    def export(self):
        # local tarballs do not need to be exported
        pass

    def clean(self):
        # TODO: clean local files from datadir (only if orig is not in datadir)
        pass

