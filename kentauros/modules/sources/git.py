"""
This sub-module contains only contains the :py:class:`GitSource` class, which has methods for
handling sources that have `source.type=git` specified and `source.orig` set to a git repository URL
in the package's configuration file.
"""


import datetime
import os
import shutil
import subprocess
import warnings

from git import Repo

from ...conntest import is_connected
from ...definitions import SourceType
from ...instance import Kentauros
from ...logcollector import LogCollector
from ...result import KtrResult

from .abstract import Source
from .source_error import SourceError

# TODO: simplify commit, branch, etc. handling to "ref" handling
# TODO: "ref" can be a branch name, commit hash, or tag!
# TODO: Introduce GitCommand class (c.f. BzrCommand)


class GitSource(Source):
    """
    This Source subclass holds information and methods for handling git sources.

    - If the `git` command is not found on the system, `self.active` is automatically set to `False`
    - For the purpose of checking connectivity to the remote server, the URL is stored in
      `self.remote`.
    - If neither `branch` nor `commit` hash has been set in the package configuration file,
      then the branch defaults to `master` (this is also written to the configuration file).
    - If a specific commit hash has been specified in the package configuration file, `shallow` is
      automatically set to `False` (this is also written to the configuration file).

    Arguments:
        Package package:  package instance this :py:class:`GitSource` belongs to
    """

    NAME = "git Source"

    def __init__(self, package):
        super().__init__(package)

        self.dest = os.path.join(self.sdir, self.spkg.get_name())
        self.stype = SourceType.GIT
        self.saved_date = None
        self.saved_commit = None

    def __str__(self) -> str:
        return "git Source for Package '" + self.spkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        """
        This method runs several checks to ensure git commands can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file
        * checks that the configuration file is consistent (i.e. shallow clone and commit checkout
          are not compatible)
        * checks if the `git` binary is installed and can be found on the system

        Returns:
            bool:   verification success
        """

        logger = LogCollector(self.name())

        success = True

        # check if the configuration file is valid
        expected_keys = ["branch", "commit", "keep", "keep_repo", "orig", "shallow"]

        for key in expected_keys:
            if key not in self.spkg.conf["git"]:
                logger.err("The [git] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # shallow clones and checking out a specific commit is not supported
        if (self.get_commit() != "HEAD") and self.get_shallow():
            logger.err("Shallow clones are not compatible with specifying a specific commit.")
            success = False

        # check if git is installed
        try:
            subprocess.check_output(["which", "git"]).decode().rstrip("\n")
        except subprocess.CalledProcessError:
            logger.log("Install git to use the specified source.")
            success = False

        return KtrResult(success, logger)

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the exported tarball should be kept
        """

        return self.spkg.conf.getboolean("git", "keep")

    def get_keep_repo(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the git repository should be kept
        """

        return self.spkg.conf.getboolean("git", "keep_repo")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream git repository URL
        """

        return self.spkg.replace_vars(self.spkg.conf.get("git", "orig"))

    def get_branch(self) -> str:
        """
        Returns:
            str:    string containing the branch that is set in the package configuration
        """

        branch = self.spkg.conf.get("git", "branch")

        if not branch:
            return "master"
        else:
            return branch

    def get_commit(self) -> str:
        """
        Returns:
            str:    string containing the commit hash that is set in the package configuration
        """

        commit = self.spkg.conf.get("git", "commit")

        if not commit:
            return "HEAD"
        else:
            return commit

    def get_shallow(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the git checkout depth should be 1 or not
        """

        return self.spkg.conf.getboolean("git", "shallow")

    def datetime(self) -> datetime.datetime:
        ktr = Kentauros()
        logger = LogCollector(self.name())

        # initialize datetime with fallback value 'now'
        dt = datetime.datetime.now()

        if not os.access(self.dest, os.R_OK):
            print(self.dest)
            state = ktr.state_read(self.spkg.get_conf_name())

            if self.saved_date is not None:
                return self.saved_date
            elif state is not None:
                if "git_last_date" in state:
                    saved_dt = state["git_last_date"]

                    if saved_dt == "":
                        logger.dbg("Saved git commit date not available. Returning 'now'.")
                        dt = datetime.datetime.now()
                    else:
                        dt = datetime.datetime.strptime(saved_dt, "%Y%m%d %H%M%S")
            else:
                raise SourceError("Sources need to be 'get' before the commit date can be read.")
        else:
            repo = Repo(self.dest)
            commit = repo.commit(self.get_commit())
            dt = commit.committed_datetime.astimezone(datetime.timezone.utc)

        warnings.warn("Log Messages might be lost!", RuntimeWarning)
        logger.print()

        self.saved_date = dt
        return dt

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

    def commit(self) -> str:
        """
        This method provides an easy way of getting the commit hash of the requested commit. It
        also stores the latest commit hash between method invocations, if the source goes away and
        the hash is needed again.

        Returns:
            str:        commit hash
        """

        ktr = Kentauros()

        # if sources are not accessible (anymore), return None or last saved commit hash
        if not os.access(self.dest, os.R_OK):
            state = ktr.state_read(self.spkg.get_conf_name())

            if self.saved_commit is not None:
                return self.saved_commit
            elif state is not None:
                if "git_last_commit" in state:
                    return state["git_last_commit"]
            else:
                raise SourceError("Sources need to be get before commit hash can be read.")

        repo = Repo(self.dest)
        commit = repo.commit(self.get_commit()).hexsha

        self.saved_commit = commit
        return commit

    def status(self) -> dict:
        """
        This method returns statistics describing this BzrSource object and its associated file(s).
        At the moment, this only includes the branch and commit hash specified in the configuration
        file.

        Returns:
            dict:   key-value pairs (property: value)
        """

        state = dict(git_branch=self.get_branch(),
                     git_commit=self.get_commit(),
                     git_last_commit=self.commit(),
                     git_last_date=self.datetime_str())

        return state

    def status_string(self) -> str:
        ktr = Kentauros()

        commit = self.commit()
        date = self.date()

        if commit == "":
            commit = ktr.state_read(self.spkg.get_conf_name())["git_last_commit"]

        if date == "":
            date = ktr.state_read(self.spkg.get_conf_name())["git_last_date"]

        string = ("git source module:\n" +
                  "  Current branch:   {}\n".format(self.get_branch()) +
                  "  Last Commit:      {}\n".format(commit) +
                  "  Last Commit Date: {}\n".format(date))

        return string

    def imports(self) -> dict:
        if os.path.exists(self.dest):
            # Sources have already been downloaded, stats can be got as usual
            return self.status()
        else:
            # Sources aren't there, last commit and date can't be determined
            return dict(git_branch=self.get_branch(),
                        git_commit=self.get_commit(),
                        git_last_commit="",
                        git_last_date="")

    def formatver(self) -> str:
        """
        This method assembles a standardised version string for git sources. This includes the
        package source base version, the git commit date and time and the first eight characters of
        the git commit hash, for example: ``11.3.0+git160422.234950.39e9cf6c``

        Returns:
            str:        nicely formatted version string
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())

        template: str = ktr.conf.get("main", "version_template_git")

        if "%{version}" in template:
            template = template.replace("%{version}", self.spkg.get_version())
        if "%{version_sep}" in template:
            template = template.replace("%{version_sep}", self.spkg.get_version_separator())
        if "%{date}" in template:
            template = template.replace("%{date}", self.date())
        if "%{time}" in template:
            template = template.replace("%{time}", self.time())
        if "%{commit}" in template:
            template = template.replace("%{commit}", self.commit())
        if "%{shortcommit}" in template:
            template = template.replace("%{shortcommit}", self.commit()[0:7])

        if "%{" in template:
            logger.log("Unrecognized variables present in git version template.")

        warnings.warn("Log Messages might be lost!", RuntimeWarning)
        logger.print()

        return template

    def get(self) -> KtrResult:
        """
        This method executes the git repository download to the package source directory. This
        respects the branch and commit set in the package configuration file.

        Returns:
            bool: *True* if successful, *False* if not or source pre-exists
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            rev = self.commit()
            logger.log("Sources already downloaded. Latest commit id:")
            logger.log(rev)
            return KtrResult(False, logger)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            logger.log("No connection to remote host detected. Cancelling source checkout.")
            return KtrResult(False, logger)

        # construct clone command
        cmd_clone = ["git", "clone"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd_clone.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd_clone.append("--verbose")

        # set --depth==1 if shallow is specified
        if self.get_shallow():
            cmd_clone.append("--depth=1")

        # set branch if specified
        if self.get_branch():
            cmd_clone.append("--branch")
            cmd_clone.append(self.get_branch())

        # set origin and destination
        cmd_clone.append(self.get_orig())
        cmd_clone.append(self.dest)

        # clone git repo from origin to destination
        logger.cmd(cmd_clone)
        subprocess.call(cmd_clone)

        # if commit is specified: checkout commit
        if self.get_commit():
            # construct checkout command
            cmd_checkout = ["git", "checkout", self.get_commit()]

            # go to git repo and remember old cwd
            prev_dir = os.getcwd()
            os.chdir(self.dest)

            # checkout commit
            logger.cmd(cmd_checkout)
            subprocess.call(cmd_checkout)

            # go to previous dir
            os.chdir(prev_dir)

        # get commit ID
        rev = self.commit()
        self.date()

        # check if checkout worked
        if self.get_commit() != "HEAD":
            if self.get_commit() != rev:
                logger.err("Something went wrong, requested commit not checked out.")
                return KtrResult(False, logger)

        # return True if successful
        return KtrResult(True, logger)

    def update(self) -> KtrResult:
        """
        This method executes a git repository update as specified in the package configuration file.
        If a specific commit has been set in the config file, this method will not attempt to
        execute an update.

        Returns:
            bool: *True* if update available and successful, *False* if not
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())

        # if specific commit is requested, do not pull updates (obviously)
        if self.get_commit() != "HEAD":
            return KtrResult(False, logger)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            logger.log("No connection to remote host detected. Cancelling source update.")
            return KtrResult(False, logger)

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
            return KtrResult(False, logger)

        # get old commit ID
        rev_old = self.commit()

        # change to git repository directory
        prev_dir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        logger.cmd(cmd)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prev_dir)

        # get new commit ID
        rev_new = self.commit()
        self.date()

        # return True if update found, False if not
        updated = rev_new != rev_old
        return KtrResult(updated, logger)

    def _remove_not_keep(self, logger: LogCollector):
        """
        This local function removes the git repository and is called after source export, if
        not keeping the repository around was specified in the configuration file.
        """

        ktr = Kentauros()

        if not self.get_keep_repo():
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert ktr.get_datadir() in self.dest
            shutil.rmtree(self.dest)
            logger.log("git repository has been deleted after exporting to tarball.")

    def export(self) -> KtrResult:
        """
        This method executes the export from the package source repository to a tarball with pretty
        file name. It also respects the `git.keep=False` setting in the package configuration file -
        the git repository will be deleted from disk after the export if this flag is set.

        Returns:
            bool:   *True* if successful or already done, *False* at failure
        """

        logger = LogCollector(self.name())

        # construct git command to export HEAD or specified commit
        cmd = ["git", "archive", self.get_commit()]

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            logger.err("Sources need to be get before they can be exported.")
            return KtrResult(False, logger)

        version = self.formatver()
        name_version = self.spkg.get_name() + "-" + version

        # add prefix
        cmd.append("--prefix=" + name_version + "/")

        file_name = os.path.join(self.sdir, name_version + ".tar.gz")

        cmd.append("--output")
        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            logger.log("Tarball has already been exported.")
            # remove git repo if keep is False
            self._remove_not_keep(logger)
            return KtrResult(True, logger)

        # remember previous directory
        prev_dir = os.getcwd()

        # change to git repository directory
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        logger.cmd(cmd)
        subprocess.call(cmd)

        # update saved rev and date
        self.commit()
        self.date()

        # remove git repo if keep is False
        self._remove_not_keep(logger)

        os.chdir(prev_dir)
        return KtrResult(True, logger)
