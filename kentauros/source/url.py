"""
"""

from kentauros.source.common import Source, SourceType

class UrlSource(Source):
    """
    kentauros.source.UrlSource
    information about and methods for tarballs available at specified URL
    """
    def __init__(self, keep=True):
        super().__init__()
        self.type = SourceType.URL
        self.keep = keep

    def get(self):
        # TODO: download source from orig to datadir
        pass

    def update(self, oldver=None, newver=None):
        # TODO: string.replace(oldversion, newversion) in orig
        # TODO: remove old download
        # TODO: download source from orig to datadir
        pass

    def refresh(self):
        # TODO: remove old download
        # TODO: download source from orig to datadir. again.
        pass

    def export(self):
        # release tarballs do not need to be exported before they can be used
        pass

    def clean(self, force=False):
        # TODO: remove downloaded file from datadir (respect keep, force)
        pass

