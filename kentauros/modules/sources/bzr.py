"""
This sub-module only contains the :py:class:`BzrSource` class, which has methods for handling
sources that have `source.type=bzr` specified and `source.orig` set to a bzr repository URL (or an
`lp:` abbreviation) in the package's configuration file.
"""


import datetime
import os
import shutil
import subprocess
import warnings

from ...conntest import is_connected
from ...definitions import SourceType
from ...instance import Kentauros
from ...logcollector import LogCollector
from ...result import KtrResult

from .abstract import Source
from .source_error import SourceError


# TODO: Use BzrCommand class for everything


class BzrCommand:
    def __init__(self, path: str, *args, bzr=None):
        if bzr is None:
            self.exec = "bzr"
        else:
            self.exec = bzr

        self.path = path
        self.args = list(args)

    def execute(self, logger: LogCollector) -> str:
        cmd = [self.exec]
        cmd.extend(self.args)

        cwd = os.getcwd()
        os.chdir(self.path)

        try:
            out = subprocess.check_output(cmd).decode().rstrip("\n")
            return out
        except subprocess.CalledProcessError as error:
            logger.err("Running the bzr command resulted in an error:")
            logger.err(repr(error))
            return ""
        finally:
            os.chdir(cwd)


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

    NAME = "bzr Source"

    def __init__(self, package):
        super().__init__(package)

        self.dest = os.path.join(self.sdir, self.spkg.get_name())
        self.stype = SourceType.BZR
        self.saved_date = None
        self.saved_rev = None

        orig = self.get_orig()

        if orig[0:3] == "lp:":
            self.remote = "https://launchpad.net"
        else:
            self.remote = orig

    def __str__(self) -> str:
        return "bzr Source for Package '" + self.spkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        """
        This method runs several checks to ensure bzr commands can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks if the `bzr` binary is installed and can be found on the system

        Returns:
            bool:   verification success
        """

        logger = LogCollector(self.name())

        success = True

        # check if the configuration file is valid
        expected_keys = ["branch", "keep", "keep_repo", "orig", "revno"]

        for key in expected_keys:
            if key not in self.spkg.conf["bzr"]:
                logger.err("The [bzr] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # check if bzr is installed
        try:
            subprocess.check_output(["which", "bzr"]).decode().rstrip("\n")
        except subprocess.CalledProcessError:
            logger.log("Install bzr to use the specified source.")
            success = False

        return KtrResult(success, logger)

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the exported tarball should be kept
        """

        return self.spkg.conf.getboolean("bzr", "keep")

    def get_keep_repo(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the bzr repository should be kept
        """

        return self.spkg.conf.getboolean("bzr", "keep_repo")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream bzr repository URL (or `lp:` link)
        """

        return self.spkg.replace_vars(self.spkg.conf.get("bzr", "orig"))

    def get_branch(self) -> str:
        """
        Returns:
            str:    string containing the branch that is set in the package configuration
        """

        return self.spkg.conf.get("bzr", "branch")

    def get_revno(self) -> str:
        """
        Returns:
            str:    string containing the revision number that is set in the package configuration
        """

        return self.spkg.conf.get("bzr", "revno")

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

        ktr = Kentauros()
        logger = LogCollector(self.name())

        # if sources are not accessible (anymore), return "" or last saved rev
        if not os.access(self.dest, os.R_OK):
            state = ktr.state_read(self.spkg.get_conf_name())

            if self.saved_rev is not None:
                return self.saved_rev
            elif state is not None:
                if "bzr_last_rev" in state:
                    return state["bzr_last_rev"]
            else:
                raise SourceError("Sources need to be get before rev can be determined.")

        cmd = ["bzr", "revno"]

        prev_dir = os.getcwd()
        os.chdir(self.dest)

        logger.cmd(cmd)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")

        os.chdir(prev_dir)

        warnings.warn("Log Messages might be lost!", RuntimeWarning)
        logger.print()

        self.saved_rev = rev
        return rev

    def datetime(self) -> datetime.datetime:
        logger = LogCollector(self.name())

        info = BzrCommand(self.dest, "version-info").execute(logger)

        for line in info:
            if line[0:6] == "date: ":
                date_string = line.replace("date: ", "")
                return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")

        logger.err("No date information present in the output of 'bzr version-info'.")
        logger.err("Assuming 'now' as fallback date/time.")

        warnings.warn("Log Messages might be lost!", RuntimeWarning)
        logger.print()

        return datetime.datetime.now()

    def datetime_str(self) -> str:
        dt = self.datetime()

        return "{:04d}{:02d}{:02d} {:02d}{:02d}{:02d}".format(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    def date(self) -> str:
        dt = self.datetime()
        return "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)

    def time(self) -> str:
        dt = self.datetime()
        return "{:02d}{:02d}{:02d}".format(dt.hour, dt.minute, dt.second)

    def status(self) -> dict:
        """
        This method returns statistics describing this BzrSource object and its associated file(s).
        At the moment, this only includes the branch and revision specified in the configuration
        file.

        Returns:
            dict:   key-value pairs (property: value)
        """

        state = dict(bzr_branch=self.get_branch(),
                     bzr_rev=self.get_revno(),
                     bzr_last_date=self.datetime_str(),
                     bzr_last_rev=self.rev())

        return state

    def status_string(self) -> str:
        ktr = Kentauros()

        rev = self.rev()

        if rev == "":
            rev = ktr.state_read(self.spkg.get_conf_name())["bzr_last_rev"]

        string = ("bzr source module:\n" +
                  "  Last Revision:    {}\n".format(rev) +
                  "  Current branch:   {}\n".format(self.get_branch()))

        return string

    def imports(self) -> dict:
        if os.path.exists(self.dest):
            # Sources have already been downloaded, stats can be got as usual
            return self.status()
        else:
            # Sources aren't there, last rev can't be determined
            return dict(bzr_branch=self.get_branch(),
                        bzr_rev=self.get_revno(),
                        bzr_last_rev="")

    def formatver(self) -> str:
        """
        This method returns a nicely formatted version string for bzr sources.

        Returns:
            str: nice version string (base version + "+bzr" + revision)
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())

        template: str = ktr.conf.get("main", "version_template_bzr")

        if "%{version}" in template:
            template = template.replace("%{version}", self.spkg.get_version())
        if "%{version_sep}" in template:
            template = template.replace("%{version_sep}", self.spkg.get_version_separator())
        if "%{date}" in template:
            template = template.replace("%{date}", self.date())
        if "%{time}" in template:
            template = template.replace("%{time}", self.time())
        if "%{revision}" in template:
            template = template.replace("%{revision}", self.rev())

        if "%{" in template:
            logger.log("Unrecognized variables present in bzr version template.")

        warnings.warn("Log Messages might be lost!", RuntimeWarning)
        logger.print()

        return template

    def get(self) -> KtrResult:
        """
        This method executes the bzr repository download to the package source directory. This
        respects the branch and revision set in the package configuration file.

        Returns:
            bool:  `True` if successful, `False` if not or source already exists
        """

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        logger = LogCollector(self.name())

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            logger.log("Sources already downloaded. Latest revision: " + str(rev))
            return KtrResult(False, logger)

        # check for connectivity to server
        if not is_connected(self.remote):
            logger.log("No connection to remote host detected. Cancelling source checkout.")
            return KtrResult(False, logger)

        # construct bzr command
        cmd = ["bzr", "branch"]

        ktr = Kentauros()

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # set origin
        if not self.get_branch():
            cmd.append(self.get_orig())
        else:
            cmd.append(self.get_orig() + "/" + self.get_branch())

        # set revision is specified
        if self.get_revno():
            cmd.append("--revision")
            cmd.append(self.get_revno())

        # set destination
        cmd.append(self.dest)

        # branch bzr repo from origin to destination
        logger.cmd(cmd)
        subprocess.call(cmd)

        # get commit ID
        rev = self.rev()

        # check if checkout worked
        if self.get_revno():
            if self.get_revno() != rev:
                logger.err("Something went wrong, requested commit not available.")
                return KtrResult(False, logger)

        # return True if successful
        return KtrResult(True, logger)

    def update(self) -> KtrResult:
        """
        This method executes a bzr repository update as specified in the package configuration file.
        If a specific revision has been set in the config file, this method will not attempt to
        execute an update.

        Returns:
            bool: `True` if update available and successful, `False` otherwise
        """

        # if specific revision is requested, do not pull updates (obviously)
        if self.get_revno():
            return KtrResult.false()

        logger = LogCollector(self.name())

        # check for connectivity to server
        if not is_connected(self.remote):
            logger.log("No connection to remote host detected. Cancelling source checkout.")
            return KtrResult(False, logger)

        # construct bzr command
        cmd = ["bzr", "pull"]

        ktr = Kentauros()

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            logger.err("Sources need to be .get() before .update() can be run.")
            return KtrResult(False, logger)

        # get old commit ID
        rev_old = self.rev()

        # change to git repository directory
        prev_dir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        logger.cmd(cmd)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prev_dir)

        # get new commit ID
        rev_new = self.rev()

        # return True if update found, False if not
        updated = rev_new != rev_old
        return KtrResult(updated, logger)

    def _remove_or_keep(self, logger: LogCollector):
        """
        This private method removes the bzr repository and is called after source export, if
        not keeping the repository around was specified in the configuration file.
        """

        ktr = Kentauros()

        if not self.get_keep_repo():
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert ktr.get_datadir() in self.dest

            shutil.rmtree(self.dest)
            logger.log("bzr repository deleted after export to tarball")

    def export(self) -> KtrResult:
        """
        This method executes the export from the package source repository to a tarball with pretty
        file name. It also respects the `bzr.keep=False` setting in the package configuration file -
        the bzr repository will be deleted from disk after the export if this flag is set.

        Returns:
            bool:       `True` if successful, `False` if not or already exported
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())

        # construct bzr command
        cmd = ["bzr", "export"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.get_revno():
            cmd.append("--revision")
            cmd.append(self.get_revno())

        # check if bzr repo exists
        if not os.access(self.dest, os.R_OK):
            logger.err("Sources need to be get before they can be exported.")
            return KtrResult(False, logger)

        version = self.formatver()
        name_version = self.spkg.get_name() + "-" + version

        file_name = os.path.join(self.sdir, name_version + ".tar.gz")

        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            logger.log("Tarball has already been exported.")
            # remove bzr repo if keep is False
            self._remove_or_keep(logger)
            return KtrResult(False, logger)

        # remember previous directory
        prev_dir = os.getcwd()

        # change to git repository directory
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        logger.cmd(cmd)
        subprocess.call(cmd)

        # update saved rev
        self.rev()

        # remove bzr repo if keep is False
        self._remove_or_keep(logger)

        os.chdir(prev_dir)
        return KtrResult(True, logger)
