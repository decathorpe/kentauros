"""
This submodule contains only contains the :py:class:`BzrSource` class, which has methods for
handling sources that have `source.type=bzr` specified and `source.orig` set to a bzr repository URL
(or an `lp:` abbreviation) in the package's configuration file.
"""


import os
import shutil
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger
from kentauros.modules.sources.abstract import Source


LOGPREFIX = "ktr/sources/bzr"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class BzrSource(Source):
    """
    This Source subclass holds information and methods for handling bzr sources.

    * If the `bzr` command is not found on the system, `self.active` is automatically set to *False*
    * For the purpose of checking connectivity to the remote server, the URL is stored in
      `self.remote`. If the specified repository is hosted on
      `launchpad.net <https://launchpad.net>`_, `lp:` will be substituted with launchpad's URL
      automatically.

    Arguments:
        Package package:    package instance this :py:class:`Source` belongs to
    """

    def __init__(self, package):
        super().__init__(package)

        self.dest = os.path.join(self.sdir, self.spkg.name)
        self.stype = SourceType.BZR
        self.saved_rev = None

        try:
            self.active = True
            subprocess.check_output(["which", "bzr"])
        except subprocess.CalledProcessError:
            KtrLogger(LOGPREFIX).log("Install bzr to use the specified source.")
            self.active = False

        if self.spkg.conf.get("source", "orig")[0:3] == "lp:":
            self.remote = "https://launchpad.net"
        else:
            self.remote = self.spkg.conf.get("source", "orig")

    def rev(self) -> str:
        """
        This method determines which revision the bzr repository associated with this
        :py:class:`BzrSource` currently is at and returns it as a string. Once run, it saves the
        last processed revision number in `self.saved_rev`, in case the revision needs to be
        determined when bzr repository might not be accessible anymore (e.g. if `bzr.keep=False` is
        set in configuration, so the repository is not kept after export to tarball).

        Returns:
            str: either revision string from repo, last stored rev string or `""` when unsuccessful
        """

        if not self.active:
            return ""

        # ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        # if sources are not accessible (anymore), return "" or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_rev is None:
                logger.err("Sources need to be get before rev can be determined.")
                return ""
            else:
                return self.saved_rev

        cmd = ["bzr", "revno"]

        prevdir = os.getcwd()
        os.chdir(self.dest)

        logger.log_command(cmd, 0)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")

        os.chdir(prevdir)

        self.saved_rev = rev
        # ktr.state_write(self.spkg.conf_name, dict(bzr_last_rev=rev))

        return rev

    def status(self) -> dict:
        """
        This method returns statistics describing this BzrSource object and its associated file(s).
        At the moment, this only includes the branch and revision specified in the configuration
        file.

        Returns:
            dict:   key-value pairs (property: value)
        """

        state = dict(bzr_branch=self.spkg.conf.get("bzr", "branch"),
                     bzr_rev=self.spkg.conf.get("bzr", "rev"))

        return state

    def formatver(self) -> str:
        """
        This method returns a nicely formatted version string for bzr sources.

        Returns:
            str: nice version string (base version + "+bzr" + revision)
        """

        if not self.active:
            return None

        ver = self.spkg.conf.get("source", "version")   # base version
        ver += "+rev"                                   # bzr prefix
        ver += self.rev()                               # revision number as string

        return ver

    def get(self) -> bool:
        """
        This method executes the bzr repository download to the package source directory. This
        respects the branch and revision set in the package configuration file.

        Returns:
            bool:  `True` if successful, `False` if not or source already exists
        """

        if not self.active:
            return False

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            logger.log("Sources already downloaded. Latest revision: " + str(rev), 1)
            return False

        # check for connectivity to server
        if not is_connected(self.remote):
            logger.log("No connection to remote host detected. Cancelling source checkout.", 2)
            return False

        # construct bzr command
        cmd = ["bzr", "branch"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # set origin
        if not self.spkg.conf.get("bzr", "branch"):
            cmd.append(self.spkg.conf.get("source", "orig"))
        else:
            cmd.append(self.spkg.conf.get("source", "orig") +
                       "/" +
                       self.spkg.conf.get("bzr", "branch"))

        # set revision is specified
        if self.spkg.conf.get("bzr", "rev"):
            cmd.append("--revision")
            cmd.append(self.spkg.conf.get("bzr", "rev"))

        # set destination
        cmd.append(self.dest)

        # branch bzr repo from orig to dest
        logger.log_command(cmd, 1)
        subprocess.call(cmd)

        # get commit ID
        rev = self.rev()

        # check if checkout worked
        if self.spkg.conf.get("bzr", "rev"):
            if self.spkg.conf.get("bzr", "rev") != rev:
                logger.err("Something went wrong, requested commit not available.")
                return False

        # return True if successful
        return True

    def update(self) -> bool:
        """
        This method executes a bzr repository update as specified in the package configuration file.
        If a specific revision has been set in the config file, this method will not attempt to
        execute an update.

        Returns:
            bool: `True` if update available and successful, `False` otherwise
        """

        if not self.active:
            return False

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        # if specific revision is requested, do not pull updates (obviously)
        if self.spkg.conf.get("bzr", "rev"):
            return False

        # check for connectivity to server
        if not is_connected(self.remote):
            logger.log("No connection to remote host detected. Cancelling source checkout.", 2)
            return False

        # construct bzr command
        cmd = ["bzr", "pull"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            logger.err("Sources need to be .get() before .update() can be run.")
            return None

        # get old commit ID
        rev_old = self.rev()

        # change to git repodir
        prevdir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        logger.log_command(cmd, 1)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prevdir)

        # get new commit ID
        rev_new = self.rev()

        # return True if update found, False if not
        return rev_new != rev_old

    def export(self) -> bool:
        """
        This method executes the export from the package source repository to a tarball with pretty
        file name. It also respects the `bzr.keep=False` setting in the package configuration file -
        the bzr repository will be deleted from disk after the export if this flag is set.

        Returns:
            bool:       `True` if successful, `False` if not or already exported
        """

        if not self.active:
            return False

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        def remove_notkeep():
            """local function for removing bzr repo after export "if not keep" """
            if not self.spkg.conf.getboolean("bzr", "keep"):
                # try to be careful with "rm -r"
                assert os.path.isabs(self.dest)
                assert ktr.conf.get_datadir() in self.dest
                shutil.rmtree(self.dest)
                logger.log("bzr repository deleted after export to tarball", 1)

        # construct bzr command
        cmd = ["bzr", "export"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.spkg.conf.get("bzr", "rev"):
            cmd.append("--revision")
            cmd.append(self.spkg.conf.get("bzr", "rev"))

        # check if bzr repo exists
        if not os.access(self.dest, os.R_OK):
            logger.err("Sources need to be get before they can be exported.")
            return False

        version = self.formatver()
        name_version = self.spkg.name + "-" + version

        file_name = os.path.join(self.sdir, name_version + ".tar.gz")

        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            logger.log("Tarball has already been exported.", 1)
            # remove bzr repo if keep is False
            remove_notkeep()
            return False

        # remember previous directory
        prevdir = os.getcwd()

        # change to git repodir
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        logger.log_command(cmd, 1)
        subprocess.call(cmd)

        # update saved rev
        self.rev()

        # remove bzr repo if keep is False
        remove_notkeep()

        os.chdir(prevdir)
        return True