"""
kentauros.source.url
contains UrlSource class and methods
this class is for handling sources that are specified by URL pointing to a tarball
"""

import os
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.init import DEBUG, VERBY, log, log_command
from kentauros.source.common import Source


LOGPREFIX1 = "ktr/source/url: "


class UrlSource(Source):
    """
    kentauros.source.url.UrlSource:
    Source subclass holding information and methods for handling URL sources
    - if wget command is not found on system, self.active = False
    - self.remote is set for checking connection to specified server
    """

    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, os.path.basename(self.conf.get("source", "orig")))
        self.type = SourceType.URL

        try:
            self.active = True
            subprocess.check_output(["which", "wget"])
        except subprocess.CalledProcessError:
            log(LOGPREFIX1 + "Install wget to use the specified source.")
            self.active = False


    def get(self):
        """
        kentauros.source.url.UrlSource.get():
        method that gets the correspondig file from URL (usually tarball)
        - returns True if download is successful
        - returns False if destination already exists
        """

        if not self.active:
            return False

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            log(LOGPREFIX1 + "Sources already downloaded.", 1)
            return False

        # check for connectivity to server
        if not is_connected(self.package.conf.get("source", "orig")):
            log("No connection to remote host detected. Cancelling source checkout.", 2)
            return False

        # construct wget commands
        cmd = ["wget"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # set origin and destination
        cmd.append(self.package.conf.get("source", "orig"))
        cmd.append("-O")
        cmd.append(self.dest)

        # wget source from orig to dest
        log_command(LOGPREFIX1, "wget", cmd, 0)
        subprocess.call(cmd)

        return True

