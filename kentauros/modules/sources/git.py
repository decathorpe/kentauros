"""
This sub-module contains only contains the :py:class:`GitSource` class, which has methods for
handling sources that have `source.type=git` specified and `source.orig` set to a git repository URL
in the package's configuration file.
"""

import configparser as cp
import datetime
import os
import shutil
import subprocess as sp

from git import Repo

from ...conntest import is_connected
from ...context import KtrContext
from ...definitions import SourceType
from ...logcollector import LogCollector
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand

from .abstract import Source
from .source_error import SourceError


class GitCommand(ShellCommand):
    NAME = "Bzr Command"

    def __init__(self, path: str, *args, git=None):
        if git is None:
            self.exec = "git"
        else:
            self.exec = git

        super().__init__(path, self.exec, *args)


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

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.dest = os.path.join(self.sdir, self.package.name)
        self.stype = SourceType.GIT
        self.saved_date: datetime.datetime = None
        self.saved_commit: str = None

    def __str__(self) -> str:
        return "git Source for Package '" + self.package.conf_name + "'"

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
        ret = KtrResult(messages=logger)

        success = True

        # check if the configuration file is valid
        expected_keys = ["keep", "keep_repo", "orig", "ref", "shallow"]

        for key in expected_keys:
            if key not in self.package.conf["git"]:
                logger.err("The [git] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        # shallow clones and checking out a specific commit is not supported
        if (self.get_ref() != "master") and self.get_shallow():
            logger.err("Shallow clones are not compatible with specifying a specific commit.")
            success = False

        # check if git is installed
        res = sp.run(["which", "git"])
        try:
            res.check_returncode()
        except sp.CalledProcessError:
            logger.log("Install git to use the specified source.")
            success = False

        return ret.submit(success)

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the exported tarball should be kept
        """

        return self.package.conf.getboolean("git", "keep")

    def get_keep_repo(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the git repository should be kept
        """

        return self.package.conf.getboolean("git", "keep_repo")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream git repository URL
        """

        return self.package.replace_vars(self.package.conf.get("git", "orig"))

    def get_ref(self) -> str:
        """
        Optionally, a specific ref (branch, tag, or commit hash) can be specified in the package
        configuration file for git sources. This method returns that string (or "master" as a
        fallback value).

        Returns:
            str:    string containing the ref that is set in the package configuration
        """

        ref = self.package.conf.get("git", "ref")

        if not ref:
            return "master"
        else:
            return ref

    def _get_commit(self) -> str:
        repo = Repo(self.dest)
        ref = repo.rev_parse(self.get_ref())
        return ref.hexsha

    def get_shallow(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the git checkout depth should be 1 or not
        """

        return self.package.conf.getboolean("git", "shallow")

    def datetime(self) -> KtrResult:
        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        # initialize datetime with fallback value 'now'
        dt = datetime.datetime.now()

        if not os.access(self.dest, os.R_OK):
            state = self.context.state.read(self.package.conf_name)

            if self.saved_date is not None:
                ret.value = self.saved_date
                return ret.submit(True)
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
            commit = repo.commit(self._get_commit())
            dt: datetime.datetime = commit.committed_datetime.astimezone(datetime.timezone.utc)

        self.saved_date = dt

        ret.value = dt
        return ret.submit(True)

    def datetime_str(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.datetime()

        if not res.success:
            return ret.submit(False)
        dt = res.value

        ret.collect(res)

        template = "{:04d}{:02d}{:02d} {:02d}{:02d}{:02d}"
        string = template.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

        ret.value = string
        ret.state["git_last_date"] = string

        return ret.submit(res.success)

    def date(self) -> KtrResult:
        ret = KtrResult()

        res = self.datetime()
        ret.collect(res)

        if res.success:
            dt = res.value
            ret.value = "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)
            return ret.submit(True)
        else:
            return ret.submit(False)

    def time(self) -> KtrResult:
        ret = KtrResult()

        res = self.datetime()
        ret.collect(res)

        if res.success:
            dt = res.value
            ret.value = "{:02d}{:02d}{:02d}".format(dt.hour, dt.minute, dt.second)
            return ret.submit(True)
        else:
            return ret.submit(False)

    def commit(self) -> KtrResult:
        """
        This method provides an easy way of getting the commit hash of the requested commit. It
        also stores the latest commit hash between method invocations, if the source goes away and
        the hash is needed again.

        Returns:
            str:        commit hash
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        if not os.access(self.dest, os.R_OK):
            state = self.context.state.read(self.package.conf_name)

            if self.saved_commit is not None:
                ret.value = self.saved_commit
                return ret.submit(True)

            elif (state is not None) and \
                    ("git_last_commit" in state) and \
                    (state["git_last_commit"] != ""):
                ret.value = state["git_last_commit"]
                return ret.submit(True)

            else:
                logger.err("Sources must be present to determine the revision.")
                return ret.submit(False)

        commit = self._get_commit()
        self.saved_commit = commit

        ret.value = commit
        ret.state["git_last_commit"] = commit
        return ret.submit(True)

    def status(self) -> KtrResult:
        """
        This method returns statistics describing this BzrSource object and its associated file(s).
        At the moment, this only includes the branch and commit hash specified in the configuration
        file.

        Returns:
            dict:   key-value pairs (property: value)
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        dt = self.datetime_str()
        ret.collect(dt)

        commit = self.commit()
        ret.collect(commit)

        version_format = self.formatver()
        ret.collect(version_format)

        ret.state["git_ref"] = self.get_ref()

        success = dt.success and commit.success and version_format.success
        return ret.submit(success)

    def status_string(self) -> KtrResult:
        ret = KtrResult()

        commit = self.commit()
        ret.collect(commit)

        date = self.datetime_str()
        ret.collect(date)

        template = """
        git source module:
          Current ref:      {ref}
          Last Commit:      {commit}
          Last Commit Date: {commit_date}
        """

        template = template.format(ref=self.get_ref())

        if commit.success:
            template = template.format(commit=commit.value)
        else:
            template = template.format(commit="Unavailable")

        if date.success:
            template = template.format(commit_date=date.value)
        else:
            template = template.format(commit_date="Unavailable")

        ret.value = template
        return ret.submit(True)

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            # Sources have already been downloaded, stats can be got as usual
            return self.status()
        else:
            # Sources aren't there, last commit and date can't be determined
            return KtrResult(True, state=dict(git_ref=self.get_ref()))

    def formatver(self) -> KtrResult:
        """
        This method assembles a standardised version string for git sources. This includes the
        package source base version, the git commit date and time and the first eight characters of
        the git commit hash, for example: ``11.3.0+160422.234950.git39e9cf6c``

        Returns:
            str:        nicely formatted version string
        """

        success = True
        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        fallback_template = "%{version}%{version_sep}%{date}.%{time}.git%{shortcommit}"

        try:
            template: str = self.context.conf.get("main", "version_template_git")
        except cp.ParsingError:
            template = fallback_template
        except cp.NoSectionError:
            template = fallback_template
        except cp.NoOptionError:
            template = fallback_template

        if "%{version}" in template:
            template = template.replace("%{version}", self.package.get_version())

        if "%{version_sep}" in template:
            template = template.replace("%{version_sep}", self.package.get_version_separator())

        if "%{date}" in template:
            res = self.date()
            ret.collect(res)

            if res.success:
                template = template.replace("%{date}", res.value)
            else:
                success = False

        if "%{time}" in template:
            res = self.time()
            ret.collect(res)

            if res.success:
                template = template.replace("%{time}", res.value)
            else:
                success = False

        # determine commit hash and shortcommit
        res = self.commit()
        ret.collect(res)

        if res.success:
            commit = res.value
        else:
            logger.log("Commit hash string could not be determined successfully.")
            return ret.submit(False)

        if "%{commit}" in template:
            template = template.replace("%{revision}", commit)

        if "%{shortcommit}" in template:
            template = template.replace("%{shortcommit}", commit[0:7])

        # look for variables that are still present
        if "%{" in template:
            logger.log("Unrecognized variables present in git version template.")

        ret.value = template
        ret.state["version_format"] = template
        return ret.submit(success)

    def _checkout(self, ref: str = None) -> KtrResult():
        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        if ref is None:
            ref = self.get_ref()

        # check out the specified ref (if it's master, nothing happens)
        # construct checkout command
        cmd_checkout = ["checkout", ref]

        # checkout commit
        logger.cmd(cmd_checkout)
        res = GitCommand(self.dest, *cmd_checkout).execute()

        if not res.success:
            logger.log("Checking out the specified ref ({}) wasn't successful.".format(ref))
            return ret.submit(False)
        else:
            return ret.submit(True)

    def get(self) -> KtrResult:
        """
        This method executes the git repository download to the package source directory. This
        respects the branch and commit set in the package configuration file.

        Returns:
            bool: *True* if successful, *False* if not or source pre-exists
        """

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            res = self.commit()
            ret.collect(res)

            if res.success:
                logger.log("Sources already downloaded. Latest commit id:")
                logger.log(res.value)
                return ret.submit(False)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            logger.log("No connection to remote host detected. Cancelling source checkout.")
            return ret.submit(False)

        # construct clone command
        cmd_clone = ["clone"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd_clone.append("--verbose")
        else:
            cmd_clone.append("--quiet")

        # set --depth==1 if shallow is specified
        if self.get_shallow():
            cmd_clone.append("--depth=1")

        # set origin and destination
        cmd_clone.append(self.get_orig())
        cmd_clone.append(self.dest)

        # clone git repo from origin to destination
        logger.cmd(cmd_clone)
        res = GitCommand(".", *cmd_clone).execute()

        if not res.success:
            logger.log("Cloning the git source repository wasn't successful.")
            ret.submit(False)

        # check out the specified ref (if it's master, nothing happens)
        res = self._checkout()
        ret.collect(res)

        if not res.success:
            logger.log("The specified ref could not be checked out successfully.")
            ret.submit(False)

        # get commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            logger.err("Commit hash could not be determined successfully.")
            return ret.submit(False)

        # get commit date/time
        res = self.date()
        ret.collect(res)

        if not res.success:
            logger.err("Commit date/time not be determined successfully.")
            return ret.submit(False)

        # return True if successful
        ret.collect(self.status())
        return ret.submit(True)

    def update(self) -> KtrResult:
        """
        This method executes a git repository update as specified in the package configuration file.
        If a specific commit has been set in the config file, this method will not attempt to
        execute an update.

        Returns:
            bool: *True* if update available and successful, *False* if not
        """

        logger = LogCollector(self.name())
        ret = KtrResult(messages=logger)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            logger.log("No connection to remote host detected. Cancelling source update.")
            return ret.submit(False)

        # construct git command
        cmd = ["pull", "--rebase", "--all"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            logger.err("Sources need to be get before an update can be run.")
            return ret.submit(False)

        # get old commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            logger.err("Commit hash could not be determined successfully.")
            return ret.submit(False)
        rev_old = res.value

        # check out master before doing updates, just to be sure
        res = self._checkout("master")
        ret.collect(res)

        if not res.success:
            logger.log("The master branch could not be checked out successfully.")
            ret.submit(False)

        # get updates
        logger.cmd(cmd)
        res = GitCommand(self.dest, *cmd).execute()

        if not res.success:
            logger.err("Pulling from remote git repository wasn't successful.")
            return ret.submit(False)

        # check out specified ref again
        res = self._checkout()
        ret.collect(res)

        if not res.success:
            logger.log("The specified ref could not be checked out successfully.")
            ret.submit(False)

        # get new commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            logger.err("Commit hash could not be determined successfully.")
            return ret.submit(False)
        rev_new = res.value

        # get new commit date/time
        res = self.date()
        ret.collect(res)

        if not res.success:
            logger.err("Commit date/time not be determined successfully.")
            return ret.submit(False)

        # return True if update found, False if not
        updated = rev_new != rev_old

        ret.collect(self.status())
        return ret.submit(updated)

    def _remove_not_keep(self, logger: LogCollector):
        """
        This local function removes the git repository and is called after source export, if
        not keeping the repository around was specified in the configuration file.
        """

        if not self.get_keep_repo():
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert self.context.get_datadir() in self.dest
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
        ret = KtrResult(messages=logger)

        # construct git command to export the specified ref
        cmd = ["archive", self.get_ref()]

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            logger.err("Sources need to be get before they can be exported.")
            return ret.submit(False)

        res = self.formatver()
        ret.collect(res)

        if not res.success:
            logger.err("Version could not be formatted successfully.")
            return ret.submit(False)
        version = res.value

        name_version = self.package.name + "-" + version

        # add prefix
        cmd.append("--prefix=" + name_version + "/")

        file_name = name_version + ".tar.gz"
        file_path = os.path.join(self.sdir, file_name)

        cmd.append("--output")
        cmd.append(file_path)

        # check if file has already been exported
        if os.path.exists(file_path):
            logger.log("Tarball has already been exported.")
            # remove git repo if keep is False
            self._remove_not_keep(logger)
            return ret.submit(True)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        logger.cmd(cmd)
        res = GitCommand(self.dest, *cmd).execute()

        if not res.success:
            logger.err("Source tarball could not be created from repository successfully.")
            return ret.submit(False)

        # update saved commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            logger.err("Commit hash could not be determined successfully.")
            return ret.submit(False)

        # update saved commit date/time
        res = self.date()
        ret.collect(res)

        if not res.success:
            logger.err("Commit date/time not be determined successfully.")
            return ret.submit(False)

        # remove git repo if keep is False
        self._remove_not_keep(logger)

        ret.collect(self.status())
        ret.state["source_files"] = [file_name]
        return ret.submit(True)
