"""
This sub-module contains only contains the :py:class:`GitSource` class, which has methods for
handling sources that have `source.type=git` specified and `source.orig` set to a git repository URL
in the package's configuration file.
"""


import os
import shutil
import subprocess

import dateutil.parser

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger
from kentauros.modules.sources.abstract import Source


LOG_PREFIX = "ktr/sources/git"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


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

    def __init__(self, package):
        super().__init__(package)

        self.dest = os.path.join(self.sdir, self.spkg.get_name())
        self.stype = SourceType.GIT

        self.saved_commit = None
        self.saved_date = None

    def __str__(self) -> str:
        return "git Source for Package '" + self.spkg.get_conf_name() + "'"

    def verify(self) -> bool:
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

        logger = KtrLogger(LOG_PREFIX)

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

        return success

    def get_keep(self) -> bool:
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

    def date(self) -> str:
        """
        This method provides an easy way of getting the date and time of the requested commit in a
        standardised format (``YYMMDD.HHmmSS``). It also stores the latest parsed date between
        method invocations, if the source goes away and the commit datetime string is needed again.

        Returns:
            str:        commit date.time string (``YYMMDD.HHmmSS``)
        """

        def prepend_zero(string):
            """
            This local function prepends '0' to one-digit time value strings.
            """

            if len(string) == 1:
                return "0" + string
            else:
                return string

        def date_str_from_raw(raw_date: str):
            """
            This local function parses a datetime object and returns a simple string.
            """

            assert isinstance(raw_date, str)

            date_obj = dateutil.parser.parse(raw_date)

            year_str = str(date_obj.year)[2:]
            month_str = prepend_zero(str(date_obj.month))
            day_str = prepend_zero(str(date_obj.day))

            hour_str = prepend_zero(str(date_obj.hour))
            minute_str = prepend_zero(str(date_obj.minute))
            second_str = prepend_zero(str(date_obj.second))

            date_str = year_str + month_str + day_str + "." + hour_str + minute_str + second_str

            return date_str

        # ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_date is None:
                logger.dbg("Sources need to be get before their age can be read.")
                return ""
            else:
                return self.saved_date

        cmd = ["git", "show", "-s", "--date=short", "--format=%cI"]

        prev_dir = os.getcwd()
        os.chdir(self.dest)

        logger.log_command(cmd, 1)
        date_raw = subprocess.check_output(cmd).decode().rstrip('\r\n')

        os.chdir(prev_dir)

        date = date_str_from_raw(date_raw)

        self.saved_date = date
        # ktr.state_write(self.spkg.get_conf_name(), dict(git_last_date=date))

        return date

    def commit(self) -> str:
        """
        This method provides an easy way of getting the commit hash of the requested commit. It
        also stores the latest commit hash between method invocations, if the source goes away and
        the hash is needed again.

        Returns:
            str:        commit hash
        """

        logger = KtrLogger(LOG_PREFIX)

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_commit is None:
                logger.dbg("Sources need to be get before commit hash can be read.")
                return ""
            else:
                return self.saved_commit

        cmd = ["git", "rev-parse", "HEAD"]

        prev_dir = os.getcwd()
        os.chdir(self.dest)

        logger.log_command(cmd, 1)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")

        os.chdir(prev_dir)

        self.saved_commit = rev
        return rev

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
                     git_last_date=self.date())

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

        # base version
        ver = self.spkg.get_version()

        # date and time of commit
        ver += "+git"
        ver += self.date()

        # first 8 chars of git commit ID
        ver += "."
        ver += self.commit()[0:8]

        return ver

    def get(self) -> bool:
        """
        This method executes the git repository download to the package source directory. This
        respects the branch and commit set in the package configuration file.

        Returns:
            bool: *True* if successful, *False* if not or source pre-exists
        """

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
        if not is_connected(self.get_orig()):
            logger.log("No connection to remote host detected. Cancelling source checkout.", 2)
            return False

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
        logger.log_command(cmd_clone, 1)
        subprocess.call(cmd_clone)

        # if commit is specified: checkout commit
        if self.get_commit():
            # construct checkout command
            cmd_checkout = ["git", "checkout", self.get_commit()]

            # go to git repo and remember old cwd
            prev_dir = os.getcwd()
            os.chdir(self.dest)

            # checkout commit
            logger.log_command(cmd_checkout, 1)
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
                return False

        # return True if successful
        return True

    def update(self) -> bool:
        """
        This method executes a git repository update as specified in the package configuration file.
        If a specific commit has been set in the config file, this method will not attempt to
        execute an update.

        Returns:
            bool: *True* if update available and successful, *False* if not
        """

        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        # if specific commit is requested, do not pull updates (obviously)
        if self.get_commit() == "HEAD":
            return False

        # check for connectivity to server
        if not is_connected(self.get_orig()):
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
        self.date()

        # return True if update found, False if not
        return rev_new != rev_old

    def export(self) -> bool:
        """
        This method executes the export from the package source repository to a tarball with pretty
        file name. It also respects the `git.keep=False` setting in the package configuration file -
        the git repository will be deleted from disk after the export if this flag is set.

        Returns:
            bool:   *True* if successful or already done, *False* at failure
        """

        ktr = Kentauros()
        logger = KtrLogger(LOG_PREFIX)

        def remove_not_keep():
            """
            This local function removes the git repository and is called after source export, if
            not keeping the repository around was specified in the configuration file.
            """

            if not self.get_keep():
                # try to be careful with "rm -r"
                assert os.path.isabs(self.dest)
                assert ktr.get_datadir() in self.dest
                shutil.rmtree(self.dest)
                logger.log("git repository has been deleted after exporting to tarball.", 1)

        # construct git command to export HEAD or specified commit
        cmd = ["git", "archive", self.get_commit()]

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            logger.err("Sources need to be get before they can be exported.")
            return False

        version = self.formatver()
        name_version = self.spkg.get_name() + "-" + version

        # add prefix
        cmd.append("--prefix=" + name_version + "/")

        file_name = os.path.join(self.sdir, name_version + ".tar.gz")

        cmd.append("--output")
        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            logger.log("Tarball has already been exported.", 1)
            # remove git repo if keep is False
            remove_not_keep()
            return True

        # remember previous directory
        prev_dir = os.getcwd()

        # change to git repository directory
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        logger.log_command(cmd, 1)
        subprocess.call(cmd)

        # update saved rev and date
        self.commit()
        self.date()

        # remove git repo if keep is False
        remove_not_keep()

        os.chdir(prev_dir)
        return True
