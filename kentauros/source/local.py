"""
# TODO: napoleon module docstring
kentauros.source.local
contains LocalSource class and methods
this class is for handling sources that are specified by file path pointing
to a tarball
"""

import os
import shutil

from kentauros.definitions import SourceType
from kentauros.instance import log

from kentauros.source.common import Source


LOGPREFIX1 = "ktr/source/local: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class LocalSource(Source):
    """
    # TODO: napoleon class docstring
    kentauros.source.local.LocalSource:
    Source subclass holding information and methods for handling local sources
    """
    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, os.path.basename(
            self.conf.get("source", "orig")))
        self.type = SourceType.LOCAL


    def formatver(self):
        # TODO: napoleon method docstring
        ver = self.conf.get("source", "version")
        return ver


    def get(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.local.LocalSource.get():
        method that gets the correspondig local file (usually tarball)
        - returns True if copying is successful
        - returns False if destination already exists
        """

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

