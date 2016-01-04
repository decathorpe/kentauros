"""
kentauros.source module
contains Source class and methods
Source class contains information about package upstream source and methods to
manipulate them.
"""

import enum

class SourceType(enum.Enum):
    """
    kentauros.source.SourceType
    enum that describes the kind of package sources supported
    """
    LOCAL = 1
    URL = 2
    SRPM = 3
    GIT = 4
    BZR = 5


class Source():
    """
    kentauros.source.Source
    class that contains information about upstream source code and
        methods that depend on it.
    """
    def __init__(self):
        self.orig = ""
        self.type = SourceType()
        self.keep = bool()

    def get(self):
        "put source into datadir"
        pass

    def update(self, oldver=None, newver=None):
        "update source in datadir from oldver to newver and update package.conf in confdir"
        pass

    def refresh(self):
        "re-put source into datadir"
        pass

    def export(self):
        "export source into tarball in datadir, if neccessary"
        pass

    def clean(self, force=False):
        "remove downloaded files in datadir (respect keep and force!)"
        pass


class LocalSource(Source):
    """
    kentauros.source.LocalSource
    information about and methods for locally available source tarballs
    """
    def __init__(self):
        super().__init__()
        self.type = SourceType.LOCAL
        self.keep = True

    def get(self):
        # TODO: copy source from orig to datadir
        # don't do anything if orig is inside datadir
        pass

    def update(self, oldver=None, newver=None):
        # local tarball does not need updating
        pass

    def refresh(self):
        # TODO: delete and re-copy source from orig to datadir
        # don't do anything if orig is inside datadir
        pass

    def export(self):
        # local tarballs do not need to be exported
        pass

    def clean(self, force=False):
        # TODO: clean local files from datadir (only if orig is not in datadir)
        pass


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
        pass

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

