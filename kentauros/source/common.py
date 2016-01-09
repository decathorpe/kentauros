"""
kentauros.source.common
contains Source class definition that is inherited by other classes
"""

import enum
import os

from kentauros.config import KTR_CONF


class SourceType(enum.Enum):
    """
    kentauros.source.common.SourceType
    enum that describes the kind of package sources supported
    """
    LOCAL = 1
    URL = 2
    SRPM = 3
    GIT = 4
    BZR = 5


class Source():
    """
    kentauros.source.common.Source
    class that contains information about upstream source code and
        methods that depend on it.
    - name: name that upstream source should get (filename or VCS repodir name)
    - sdir: directory that contains all source files of the package
    - dest: destination where upstream source is put (file or directory)
    - orig: origin of upstream sources (URL to file, git repo, etc.)
    - type: determines type of upstream source
    - keep: determines if sources are kept between builds
    """
    def __init__(self, name):
        self.sdir = os.path.join(KTR_CONF.datadir, name)
        self.dest = os.path.join(self.sdir, name)

        self.keep = bool()
        self.orig = ""
        self.type = None
        self.version = ""

    def clean(self, force=False):
        "remove downloaded files in datadir (respect keep and force!)"
        pass

    def export(self):
        "export source into tarball in datadir, if neccessary"
        pass

    def get(self):
        "put source into datadir"
        pass

    def refresh(self):
        "re-put source into datadir"
        pass

    def update(self, oldver=None, newver=None):
        "update source in datadir from oldver to newver and update package.conf in confdir"
        pass

    def formatver(self):
        "returns formatted version string, depending on SourceType"
        pass

