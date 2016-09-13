"""
This submodule contains only contains the :py:class:`LocalSource` class, which has methods for
handling sources that have `source.type=local` specified and `source.orig` set to an absolute path
of a local file in the package's configuration file.
"""


import os
import shutil

from kentauros.definitions import SourceType
from kentauros.instance import Kentauros

from kentauros.sources.src_abstract import Source


LOGPREFIX = "ktr/sources/local"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class LocalSource(Source):
    """
    This :py:class:`Source` subclass provides handling of local sources.

    Arguments:
        Package package:    package instance this source belongs to
    """

    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, os.path.basename(self.spkg.conf.get("source", "orig")))
        self.type = SourceType.LOCAL

    def status(self) -> dict:
        return dict()

    def get(self) -> bool:
        """
        This method attempts to copy the specified source from the location specified in the package
        configuration file to the determined destination. If the destination file already exists,
        nothing will be done.

        Returns:
            bool:   *True* if source was copied successfully, *False* if not
        """

        ktr = Kentauros(LOGPREFIX)

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            ktr.log("Sources already present.", 1)
            return False

        # copy file from orig to dest
        shutil.copy2(self.spkg.conf.get("source", "orig"), self.dest)

        return True

    def export(self) -> bool:
        return True

    def update(self) -> bool:
        return True
