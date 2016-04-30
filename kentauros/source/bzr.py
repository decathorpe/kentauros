"""
This submodule contains only contains the :py:class:`BzrSource` class, which has
methods for handling sources that have `source.type=bzr` specified and
`source.orig` set to a bzr repository URL (or an `lp:` abbreviation) in the
package's configuration file.
"""

# TODO: rename module to src_bzr.py

import os
import shutil
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.instance import Kentauros, err, log, log_command

from kentauros.source.source import Source


LOGPREFIX1 = "ktr/source/bzr: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class BzrSource(Source):
    """
    This Source subclass holds information and methods for handling bzr sources.

    * If the `bzr` command is not found on the system, `self.active` is
      automatically set to `False`.
    * For the purpose of checking connectivity to the remote server, the URL is
      stored in `self.remote`. If the specified repository is hosted on
      `launchpad.net <https://launchpad.net>`_, `lp:` will be substituted with
      launchpad's URL automatically.

    Arguments:
        Package package:    package instance this `Source` belongs to
    """

    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, self.name)
        self.type = SourceType.BZR
        self.saved_rev = None

        try:
            self.active = True
            subprocess.check_output(["which", "bzr"])
        except subprocess.CalledProcessError:
            log(LOGPREFIX1 + "Install bzr to use the specified source.")
            self.active = False

        if self.conf.get("source", "orig")[0:3] == "lp:":
            self.remote = "https://launchpad.net"
        else:
            self.remote = self.conf.get("source", "orig")


    def rev(self) -> str:
        """
        This method determines which revision the bzr repository associated with
        this BzrSource currently is at and returns it as a string. Once run, it
        saves the last processed revision number in `self.saved_rev`, in
        case the revision needs to be determined when bzr repository might not
        be accessible anymore (e.g. if `bzr.keep=False` is set in
        configuration, so the repository is not kept after export to tarball).

        Returns:
            str: either successfully determined revision string from \
                 repository, last stored rev string or `""` when not
        """

        if not self.active:
            return ""

        cmd = ["bzr", "revno"]

        prevdir = os.getcwd()

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_rev is "":
                err("Sources need to be get before rev can be determined.")
                return ""
            else:
                return self.saved_rev

        os.chdir(self.dest)
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")
        os.chdir(prevdir)

        self.saved_rev = rev
        return rev


    def formatver(self) -> str:
        """
        This method returns a nicely formatted version string for bzr sources.

        Returns:
            str: nice version string (base version + "~bzr" + revision)
        """

        if not self.active:
            return None

        ver = self.conf.get("source", "version")    # base version
        ver += "~rev"                               # bzr prefix
        ver += self.rev()                           # revision number as string
        return ver


    def get(self) -> bool:
        """
        This method executes the bzr repository download to the package source
        directory. This respects the branch and revision set in the package
        configuration file.

        Returns:
            bool:  `True` if successful, `False` if not or source already exists
        """

        if not self.active:
            return False

        ktr = Kentauros()

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            log(LOGPREFIX1 + "Sources already downloaded. Latest commit id:", 1)
            log(LOGPREFIX1 + rev, 1)
            return False

        # check for connectivity to server
        if not is_connected(self.remote):
            log("No connection to remote host detected. " + \
                "Cancelling source checkout.", 2)
            return False

        # construct bzr command
        cmd = ["bzr", "branch"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # set origin
        if not self.get("bzr", "branch"):
            cmd.append(self.conf.get("source", "orig"))
        else:
            cmd.append(self.conf.get("source", "orig") + "/" + \
                       self.conf.get("bzr", "branch"))

        # set revision is specified
        if self.conf.get("bzr", "rev"):
            cmd.append("--revision")
            cmd.append(self.conf.get("bzr", "rev"))

        # set destination
        cmd.append(self.dest)

        # branch bzr repo from orig to dest
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        subprocess.call(cmd)

        # get commit ID
        rev = self.rev()

        # check if checkout worked
        if self.conf.get("bzr", "rev"):
            if self.conf.get("bzr", "rev") != rev:
                err(LOGPREFIX1 + \
                    "Something went wrong, requested commit not available.")
                return False

        # return True if successful
        return True


    def update(self) -> bool:
        """
        This method executes a bzr repository update as specified in the package
        configuration file. If a specific revision has been set in the config
        file, this method will not attempt to execute an update.

        Returns:
            bool: `True` if update available and successful, `False` otherwise
        """

        if not self.active:
            return False

        ktr = Kentauros()

        # if specific revision is requested, do not pull updates (obviously)
        if self.conf.get("bzr", "rev"):
            return False

        # check for connectivity to server
        if not is_connected(self.remote):
            log("No connection to remote host detected. " + \
                "Cancelling source checkout.", 2)
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
            err(LOGPREFIX1 + \
                "Sources need to be .get() before .update() can be run.")
            return None

        # get old commit ID
        rev_old = self.rev()

        # change to git repodir
        prevdir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prevdir)

        # get new commit ID
        rev_new = self.rev()

        # return True if update found, False if not
        return rev_new != rev_old


    def export(self) -> bool:
        """
        This method executes the export from the package source repository to a
        tarball with pretty file name. It also respects the `bzr.keep=False`
        setting in the package configuration file - the bzr repository will be
        deleted from disk after the export if this flag is set.

        Returns:
            bool:       `True` if successful, `False` if not or already exported
        """

        if not self.active:
            return False

        ktr = Kentauros()

        def remove_notkeep():
            "local function for removing bzr repo after export if not keep"
            if not self.conf.getboolean("bzr", "keep"):
                # try to be careful with "rm -r"
                assert os.path.isabs(self.dest)
                assert ktr.conf.datadir in self.dest
                shutil.rmtree(self.dest)
                log(LOGPREFIX1 + "bzr repo deleted after export to tarball", 1)

        # construct bzr command
        cmd = ["bzr", "export"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.conf.get("bzr", "rev"):
            cmd.append("--revision")
            cmd.append(self.conf.get("bzr", "rev"))

        # check if bzr repo exists
        if not os.access(self.dest, os.R_OK):
            err(LOGPREFIX1 + \
                "Sources need to be get before they can be exported.")
            return False

        version = self.formatver()
        name_version = self.name + "-" + version

        file_name = os.path.join(ktr.conf.datadir,
                                 self.name,
                                 name_version + ".tar.gz")

        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            log(LOGPREFIX1 + "Tarball has already been exported.", 1)
            # remove bzr repo if keep is False
            remove_notkeep()
            return False

        # remember previous directory
        prevdir = os.getcwd()

        # change to git repodir
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        log_command(LOGPREFIX1, "bzr", cmd, 0)
        subprocess.call(cmd)

        # update saved rev
        self.rev()

        # remove bzr repo if keep is False
        remove_notkeep()

        os.chdir(prevdir)
        return True

