"""
This sub-module contains only contains the :py:class:`UrlSource` class, which has methods for
handling sources that have `source.type=url` specified and `source.orig` set to a URL of a tarball
in the package's configuration file.
"""

import os
import subprocess as sp

from ...conntest import is_connected
from ...context import KtrContext
from ...definitions import SourceType
from ...package import KtrPackage
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

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.stype = SourceType.URL

        state = self.context.state.read(self.package.conf_name)

        if state is None:
            self.last_version = None
        elif "url_last_version" in state:
            self.last_version = state["url_last_version"]
        else:
            self.last_version = None

    def __str__(self) -> str:
        return "URL Source for Package '" + self.package.conf_name + "'"

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

        ret = KtrResult(name=self.name())
        success = True

        # check if the configuration file is valid
        expected_keys = ["keep", "orig"]

        for key in expected_keys:
            if key not in self.package.conf["url"]:
                template = "The [url] section in the package's .conf file doesn't set the {} key."
                ret.messages.err(template.format(key))
                success = False

        # check if wget is installed

        res = sp.run(["which", "wget"], stdout=sp.PIPE, stderr=sp.STDOUT)

        try:
            res.check_returncode()
        except sp.CalledProcessError:
            ret.messages.log("Install wget to use the specified source.")
            success = False

        return ret.submit(success)

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the downloaded file should be kept
        """

        return self.package.conf.getboolean("url", "keep")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream file URL
        """

        return self.package.replace_vars(self.package.conf.get("url", "orig"))

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
        state = self.context.state.read(self.package.conf_name)

        if "url_last_version" in state:
            string = ("url source module:\n" +
                      "  Last download:    {}\n".format(state["url_last_version"]))
        else:
            string = ("url source module:\n" +
                      "  Last download:    None\n")

        return KtrResult(True, string, state=state)

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            return KtrResult(True, state=dict(url_last_version=self.package.get_version()))
        else:
            return KtrResult(True)

    def get(self) -> KtrResult:
        """
        This method executes the download of the file specified by the URL to the package source
        directory.

        Returns:
            bool:  *True* if successful, *False* if not or source already exists
        """

        ret = KtrResult(name=self.name())

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            ret.messages.log("Sources already downloaded.")
            return ret.submit(True)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            ret.messages.log("No connection to remote host detected. Cancelling source download.")
            return ret.submit(False)

        # construct wget commands
        cmd = ["wget"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        # set origin and destination
        cmd.append(self.get_orig())
        cmd.append("-O")
        cmd.append(self.dest)

        # wget source from origin to destination
        ret.messages.cmd(cmd)
        res: sp.CompletedProcess = sp.run(cmd,
                                          stdout=sp.PIPE,
                                          stderr=sp.STDOUT)

        if res.returncode != 0:
            ret.messages.lst("Sources could not be downloaded successfully. wget output:",
                             res.stdout.decode().split("\n"))
            return ret.submit(False)

        success = (ret == 0)

        if success:
            self.last_version = self.package.get_version()

        ret.state["source_files"] = [os.path.basename(self.get_orig())]
        return ret.submit(success)

    def update(self) -> KtrResult:
        return KtrResult(False)

    def export(self) -> KtrResult:
        return KtrResult(True)
