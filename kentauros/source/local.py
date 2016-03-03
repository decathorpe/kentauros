"""
kentauros.source.local
contains LocalSource class and methods
this class is for handling sources that are specified by file path pointing to a tarball
"""

import os
import shutil

from kentauros.definitions import SourceType
from kentauros.source.common import Source
from kentauros.init import log


LOGPREFIX1 = "ktr/source/local: "


class LocalSource(Source):
    """
    kentauros.source.LocalSource
    information about and methods for locally available source tarballs
    """
    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, os.path.basename(self.conf.get("source", "orig")))
        self.type = SourceType.LOCAL


    def formatver(self):
        ver = self.conf.get("source", "version")
        return ver


    def get(self):
        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            log(LOGPREFIX1 + "Sources already present.", 1)
            return False

        # copy file from orig to dest
        shutil.copy2(self.conf.get("source", "orig"), self.dest)

        return True


    def update(self):
        # local tarball does not need updating
        pass

