"""
This submodule contains only contains the :py:class:`LocalSource` class, which
has methods for handling sources that have ``source.type=local`` specified and
``source.orig`` set to an absolute path of a local file in the package's
configuration file.
"""


import os
import shutil

from kentauros.definitions import SourceType
from kentauros.instance import log

from kentauros.source.source import Source


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


    def formatver(self) -> str:
        # TODO: napoleon method docstring
        ver = self.conf.get("source", "version")
        return ver


    def get(self) -> bool:
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

