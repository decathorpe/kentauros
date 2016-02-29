"""
kentauros.source.common
contains Source class definition that is inherited by other classes
"""

import os
import shutil

from kentauros.init import log
from kentauros.config import KTR_CONF


LOGPREFIX1 = "ktr/source: "


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
    def __init__(self, package):
        self.package = package
        self.conf = package.conf
        self.name = self.conf['package']['name']
        self.sdir = os.path.join(KTR_CONF['main']['datadir'], self.name)
        self.type = None

    def clean(self):
        "remove downloaded files in datadir (respect keep and force!)"
        if not os.access(self.sdir, os.R_OK):
            log(LOGPREFIX1 + "Nothing here to be cleaned.", 0)
        else:
            # try to be careful with "rm -r"
            assert os.path.isabs(self.sdir)
            assert KTR_CONF['main']['datadir'] in self.sdir
            shutil.rmtree(self.sdir)

    def export(self):
        "export source into tarball in datadir, if neccessary"
        pass

    def get(self):
        "put source into datadir"
        pass

    def refresh(self):
        "re-put source into datadir"
        self.clean()
        self.get()

    def update(self):
        "update source in datadir from oldver to newver and update package.conf in confdir"
        pass

    def formatver(self):
        "returns formatted version string, depending on SourceType"
        pass

