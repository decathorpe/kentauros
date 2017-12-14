"""
This sub-module contains only contains the :py:class:`UrlSource` class, which has methods for
handling sources that have `source.type=url` specified and `source.orig` set to a URL of a tarball
in the package's configuration file.
"""


import os
import subprocess

from ...conntest import is_connected
from ...definitions import SourceType
from ...instance import Kentauros
from ...logcollector import LogCollector
from ...result import KtrResult

from .abstract import Source


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

    NAME = "URL Source"

    def __init__(self, package):
        super().__init__(package)

        ktr = Kentauros()

        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.stype = SourceType.URL

        state = ktr.state_read(self.spkg.get_conf_name())

        if state is None:
            self.last_version = None
        elif "url_last_version" in state:
            self.last_version = state["url_last_version"]
        else:
            self.last_version = None

    def __str__(self) -> str:
        return "URL Source for Package '" + self.spkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        """
        This method runs several checks to ensure wget commands can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `wget` binary is installed and can be found on the system

        Returns:
            bool:   verification success
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

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
            success = False

        return ret.submit(success)

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the downloaded file should be kept
        """

        return self.spkg.conf.getboolean("url", "keep")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream file URL
        """

        return self.spkg.replace_vars(self.spkg.conf.get("url", "orig"))

    def status(self) -> KtrResult:
        """
        This method returns a dictionary containing the package version of the tarball that was last
        downloaded (as the status is only updated after successful actions).

        Returns:
            dict:   key-value pairs (property: value)
        """

        if self.last_version is None:
            return KtrResult(True)
        else:
            state = dict(url_last_version=self.last_version)
            return KtrResult(True, state=state)

    def status_string(self) -> KtrResult:
        ktr = Kentauros()

        state = ktr.state_read(self.spkg.get_conf_name())

        if "url_last_version" in state:
            string = ("url source module:\n" +
                      "  Last download:    {}\n".format(state["url_last_version"]))
        else:
            string = ("url source module:\n" +
                      "  Last download:    None\n")

        return KtrResult(True, string, str, state=state)

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            return KtrResult(True, state=dict(url_last_version=self.spkg.get_version()))
        else:
            return KtrResult(True)

    def get(self) -> KtrResult:
        """
        This method executes the download of the file specified by the URL to the package source
        directory.

        Returns:
            bool:  *True* if successful, *False* if not or source already exists
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            logger.log("Sources already downloaded.")
            return ret.submit(True)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            logger.log("No connection to remote host detected. Cancelling source download.")
            return ret.submit(False)

        # construct wget commands
        cmd = ["wget"]

        ktr = Kentauros()

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # set origin and destination
        cmd.append(self.get_orig())
        cmd.append("-O")
        cmd.append(self.dest)

        # wget source from origin to destination
        logger.cmd(cmd)
        res: subprocess.CompletedProcess = subprocess.run(cmd, stderr=subprocess.STDOUT)

        if res.returncode != 0:
            logger.lst("Sources could not be downloaded successfully. wget output:",
                       res.stdout.decode().split("\n"))
            return ret.submit(False)

        success = (ret == 0)

        if success:
            self.last_version = self.spkg.get_version()

        return ret.submit(success)

    def update(self) -> KtrResult:
        return KtrResult(False)

    def export(self) -> KtrResult:
        return KtrResult(True)
