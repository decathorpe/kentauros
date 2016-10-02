"""
This submodule contains only contains the :py:class:`UrlSource` class, which has methods for
handling sources that have `source.type=url` specified and `source.orig` set to a URL of a tarball
in the package's configuration file.
"""


import os
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger
from kentauros.modules.sources.abstract import Source


LOGPREFIX = "ktr/sources/url"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class UrlSource(Source):
    """
    This Source subclass holds information and methods for handling URL sources.

    * If the `wget` command is not found on the system, `self.active` is automatically set to
      *False*.
    * For the purpose of checking connectivity to the remote server, the URL is stored in
      `self.remote`.

    Arguments:
        Package package:    package instance this :py:class:`UrlSource` belongs to
    """

    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, os.path.basename(
            self.spkg.conf.get("source", "orig")))
        self.stype = SourceType.URL

        logger = KtrLogger(LOGPREFIX)

        try:
            self.active = True
            subprocess.check_output(["which", "wget"])
        except subprocess.CalledProcessError:
            logger.log("Install wget to use the specified source.")
            self.active = False

    def status(self) -> dict:
        return dict()

    def get(self) -> bool:
        """
        This method executes the download of the file specified by the URL to the package source
        directory.

        Returns:
            bool:  *True* if successful, *False* if not or source already exists
        """

        if not self.active:
            return False

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            logger.log("Sources already downloaded.", 1)
            return False

        # check for connectivity to server
        if not is_connected(self.spkg.conf.get("source", "orig")):
            logger.log("No connection to remote host detected. Cancelling source download.", 2)
            return False

        # construct wget commands
        cmd = ["wget"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # set origin and destination
        cmd.append(self.spkg.conf.get("source", "orig"))
        cmd.append("-O")
        cmd.append(self.dest)

        # wget source from orig to dest
        logger.log_command(cmd, 1)
        subprocess.call(cmd)

        return True

    def update(self) -> bool:
        return True

    def export(self) -> bool:
        return True
