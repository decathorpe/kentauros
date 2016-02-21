"""
kentauros.source.common
contains Source class definition that is inherited by other classes
"""

from enum import Enum
import os

from kentauros.config import KTR_CONF


class SourceType(Enum):
    """
    kentauros.source.common.SourceType
    enum that describes the kind of package sources supported
    """
    LOCAL = 1
    URL = 2
    GIT = 3
    BZR = 4


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
    def __init__(self, pkgconfig):
        self.conf = pkgconfig

        self.name = pkgconfig['package']['name']
        self.sdir = os.path.join(KTR_CONF['main']['datadir'], self.name)
        self.dest = os.path.join(self.sdir, self.name)

        self.type = None

    def get_keep(self):
        """
        kentauros.source.Source.get_keep():
        get from config if source tarball shall be kept
        """
        return bool(self.conf['source']['keep'])

    def get_orig(self):
        """
        kentauros.source.Source.get_orig():
        get upstream source location from config
        """
        return self.conf['source']['orig']

    def get_version(self):
        """
        kentauros.source.Source.get_version():
        get upstream source version from config
        """
        return self.conf['source']['version']

    def set_keep(self, keep):
        """
        kentauros.source.Source.set_keep():
        set config value that determines if source tarball is kept
        """
        self.conf['source']['keep'] = keep

    def set_orig(self, orig):
        """
        kentauros.source.Source.set_orig():
        set config value that determines upstream source location
        """
        self.conf['source']['orig'] = orig

    def set_version(self, version):
        """
        kentauros.source.Source.set_version():
        set config value that determines upstream source version
        """
        self.conf['source']['version'] = version

    def clean(self):
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

    def update(self):
        "update source in datadir from oldver to newver and update package.conf in confdir"
        pass

    def formatver(self):
        "returns formatted version string, depending on SourceType"
        pass

