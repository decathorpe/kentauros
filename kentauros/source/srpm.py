"""
kentauros.source.srpm
contains LocalSource class and methods
this class is for handling sources that are specified by file path pointing to a tarball
"""

from kentauros.source.common import Source, SourceType


class SrpmSource(Source):
    """
    kentauros.source.SrpmSource
    information about and methods for SRPMs available from URL
    """
    def __init__(self):
        super().__init__()
        self.type = SourceType.SRPM
        self.keep = True

    def get(self):
        # TODO: copy source from orig to datadir
        pass

    def update(self, oldver=None, newver=None):
        # TODO: check if version is different to the last downloaded one
        pass

    def refresh(self):
        # TODO: delete and re-copy source from orig to datadir
        # don't do anything if orig is inside datadir
        pass

    def export(self):
        # SRPMs do not need to be exported
        pass

    def clean(self, force=False):
        # TODO: clean local files from datadir (only if orig is not in datadir)
        pass

