"""
kentauros.source.url
contains UrlSource class and methods
this class is for handling sources that are specified by URL pointing to a tarball
"""

import os
import subprocess

from kentauros.definitions import SourceType
from kentauros.init import DEBUG, VERBY, log, log_command
from kentauros.source.common import Source


LOGPREFIX1 = "ktr/source/url: "


class UrlSource(Source):
    """
    kentauros.source.UrlSource
    information about and methods for tarballs available at specified URL
    """
    def __init__(self, pkgconfig):
        super().__init__(pkgconfig)
        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.type = SourceType.URL


    def formatver(self):
        ver = self.get_version()    # base version
        return ver


    def get(self):
        """
        kentauros.source.url.UrlSource.get()
        get sources from specified URL
        """

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, quit
        if os.access(self.dest, os.R_OK):
            log(LOGPREFIX1 + "Sources already downloaded.", 1)
            return None

        # construct wget commands
        cmd = ["wget"]

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # set origin and destination
        cmd.append(self.get_orig())
        cmd.append("-O")
        cmd.append(self.dest)

        # wget source from orig to dest
        log_command(LOGPREFIX1, "wget", cmd, 0)
        subprocess.call(cmd)


    def update(self):
        return False

