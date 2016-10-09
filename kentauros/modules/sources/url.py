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

        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.stype = SourceType.URL

    def __str__(self) -> str:
        return "URL Source for Package '" + self.spkg.get_conf_name() + "'"

    def verify(self) -> bool:
        """
        This method runs several checks to ensure wget commands can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `wget` binary is installed and can be found on the system

        Returns:
            bool:   verification success
        """

        logger = KtrLogger(LOGPREFIX)

        success = True

        # check if the configuration file is valid
        expected_keys = ["keep", "orig"]

        for key in expected_keys:
            if key not in self.spkg.conf["url"]:
                logger.err("The [url] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # check if wget is installed
        try:
            subprocess.check_output(["which", "wget"])
        except subprocess.CalledProcessError:
            logger.log("Install wget to use the specified source.")

        return success

    def get_keep(self) -> bool:
        return self.spkg.conf.getboolean("url", "keep")

    def get_keep_repo(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the downloaded file should be kept
        """

        return self.spkg.conf.getboolean("url", "keep_repo")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream file URL
        """

        return self.spkg.conf.get("url", "orig")

    def status(self) -> dict:
        return dict()

    def status_string(self) -> str:
        return str()

    def imports(self) -> dict:
        return dict()

    def get(self) -> bool:
        """
        This method executes the download of the file specified by the URL to the package source
        directory.

        Returns:
            bool:  *True* if successful, *False* if not or source already exists
        """

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
        if not is_connected(self.get_orig()):
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
        cmd.append(self.get_orig())
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
