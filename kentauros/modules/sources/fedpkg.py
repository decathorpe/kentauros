"""
This sub-module only contains the :py:class:`FedPkgSource` class, which has methods for handling
sources of official fedora packages.
"""


import glob
import os
import shutil
import subprocess

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger

from kentauros.modules.sources.abstract import Source
from kentauros.modules.sources.source_error import SourceError


LOG_PREFIX = "ktr/sources/fedpkg"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class FedPkgSource(Source):
    """
    This Source subclass holds information and methods for handling official fedora package's
    sources.

    - If the `fedpkg` or `git` command is not found on the system, this module will fail validation.
    - If no connection to the server at `https://src.fedoraproject.org` can be established, no
      actions will be executed.

    Arguments:
        Package package:    package instance this :py:class:`FedPkgSource` belongs to
    """

    def __init__(self, package):
        super().__init__(package)

        self.dest = os.path.join(self.sdir, self.get_orig())
        self.stype = SourceType.FEDPKG

    def __str__(self) -> str:
        return "fedpkg Source for Package '" + self.spkg.get_conf_name() + "'"

    def verify(self) -> bool:
        """
        This method runs several checks to ensure fedpkg commands can run successfully. It is
        automatically executed at package initialization. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `fedpkg` and `git` binaries are installed and can be found on the system

        Returns:
            bool:   verification success
        """

        logger = KtrLogger(LOG_PREFIX)

        success = True

        # check if the configuration file is valid
        expected_keys = ["name"]

        for key in expected_keys:
            if key not in self.spkg.conf["fedpkg"]:
                logger.err("The [fedpkg] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # check if fedpkg is installed
        try:
            subprocess.check_output(["which", "fedpkg"]).decode().rstrip("\n")
        except subprocess.CalledProcessError:
            logger.log("Install fedpkg to use the specified source.")
            success = False

        # check if git is installed
        try:
            subprocess.check_output(["which", "git"]).decode().rstrip("\n")
        except subprocess.CalledProcessError:
            logger.log("Install git to use the specified source.")
            success = False

        return success

    def get_keep(self) -> bool:
        return True

    def get_orig(self) -> str:
        return self.spkg.conf.get("fedpkg", "name")

    def commit(self) -> str:
        """
        This method provides an easy way of getting the commit hash of the requested commit.

        Returns:
            str:    commit hash
        """

        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        # if sources are not accessible, return last saved commit hash
        if not os.access(self.dest, os.R_OK):
            state = ktr.state_read(self.spkg.get_conf_name())

            if state is None:
                raise SourceError("Sources need to be get before the commit hash can be read.")
            else:
                return state["fedpkg_last_commit"]

        cmd = ["git", "rev-parse", "HEAD"]

        prev_dir = os.getcwd()
        os.chdir(self.dest)

        logger.log_command(cmd, 1)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")

        os.chdir(prev_dir)

        return rev

    def status(self) -> dict:
        state = dict(fedpkg_last_commit=self.commit())
        return state

    def status_string(self) -> str:
        commit = self.commit()

        string = ("fedpkg source module:\n" +
                  "  Last Commit:      {}\n".format(commit))

        return string

    def imports(self) -> dict:
        if os.path.exists(self.dest):
            return self.status()
        else:
            return dict(fedpkg_last_commit="")

    def formatver(self) -> str:
        # get version from the .spec file
        raise NotImplementedError()

    def get(self) -> bool:
        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            rev = self.commit()
            logger.log("Sources already downloaded. Latest commit id:", 2)
            logger.log(rev, 2)
            return False

        # check for connectivity to server
        if not is_connected("https://src.fedoraproject.org"):
            logger.log("No connection to remote host detected. Cancelling source checkout.", 2)
            return False

        # construct fedpkg command
        cmd_clone = ["fedpkg"]

        if (ktr.verby == 2) and not ktr.debug:
            cmd_clone.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd_clone.append("--verbose")

        cmd_clone.append("clone")
        cmd_clone.append(self.get_orig())

        prev_dir = os.getcwd()
        os.chdir(self.sdir)

        logger.log_command(cmd_clone, 1)

        try:
            subprocess.check_call(cmd_clone)
        except subprocess.CalledProcessError:
            logger.err("fedpkg clone unsuccessful.")
            return False
        finally:
            os.chdir(prev_dir)

        return True

    def update(self) -> bool:
        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        if not is_connected("https://src.fedoraproject.org"):
            logger.log("No connection to remote host detected. Cancelling source update.", 2)
            return False

        # construct git command
        cmd = ["git", "pull", "--rebase"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            logger.err("Sources need to be get before an update can be run.")
            return False

        # get old commit ID
        rev_old = self.commit()

        # change to git repository directory
        prev_dir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        logger.log_command(cmd, 1)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prev_dir)

        # get new commit ID
        rev_new = self.commit()

        # return True if update found, False if not
        return rev_new != rev_old

    def export(self) -> bool:
        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        # TODO: do the stuff below for all specified branches

        cmd = ["fedpkg", "srpm"]

        if not os.access(self.dest, os.R_OK):
            logger.err("Sources need to be get before they can be exported.")
            return False

        # remember previous directory
        prev_dir = os.getcwd()

        # change to git repository directory
        os.chdir(self.dest)

        # build .src.rpm file in current directory
        logger.log_command(cmd, 1)
        ret = subprocess.call(cmd)

        srpms = glob.glob("*.src.rpm")

        for srpm in srpms:
            logger.log("Copying srpm file: " + srpm)

            path = os.path.join(os.getcwd(), srpm)
            dest = os.path.join(ktr.get_packdir(), self.spkg.get_conf_name())
            os.makedirs(dest, exist_ok=True)

            shutil.move(path, os.path.join(dest, srpm))

        os.chdir(prev_dir)
        return not ret
