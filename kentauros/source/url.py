"""
This submodule contains only contains the :py:class:`UrlSource` class, which
has methods for handling sources that have ``source.type=url`` specified and
``source.orig`` set to a URL of a tarball in the package's configuration file.
"""

# TODO: rename module to src_url.py

import os
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.instance import Kentauros, log, log_command

from kentauros.source.source import Source


LOGPREFIX1 = "ktr/source/url: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class UrlSource(Source):
    """
    This Source subclass holds information and methods for handling URL sources.

    * If the ``wget`` command is not found on the system, ``self.active`` is
      automatically set to ``False``.
    * For the purpose of checking connectivity to the remote server, the URL is
      stored in ``self.remote``.

    Arguments:
        Package package:    package instance this `Source` belongs to
    """

    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, os.path.basename(
            self.conf.get("source", "orig")))
        self.type = SourceType.URL

        try:
            self.active = True
            subprocess.check_output(["which", "wget"])
        except subprocess.CalledProcessError:
            log(LOGPREFIX1 + "Install wget to use the specified source.")
            self.active = False


    def get(self) -> bool:
        """
        This method executes the download of the file specified by the URL to
        the package source directory.

        Returns:
            bool:  `True` if successful, `False` if not or source already exists
        """

        if not self.active:
            return False

        ktr = Kentauros()

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            log(LOGPREFIX1 + "Sources already downloaded.", 1)
            return False

        # check for connectivity to server
        if not is_connected(self.package.conf.get("source", "orig")):
            log("No connection to remote host detected. " + \
                "Cancelling source checkout.", 2)
            return False

        # construct wget commands
        cmd = ["wget"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # set origin and destination
        cmd.append(self.package.conf.get("source", "orig"))
        cmd.append("-O")
        cmd.append(self.dest)

        # wget source from orig to dest
        log_command(LOGPREFIX1, "wget", cmd, 0)
        subprocess.call(cmd)

        return True

