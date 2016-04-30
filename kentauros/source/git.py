"""
This submodule contains only contains the :py:class:`GitSource` class, which has
methods for handling sources that have ``source.type=git`` specified and
``source.orig`` set to a git repository URL in the package's configuration file.
"""

# TODO: rename module to src_git.py

import os
import shutil
import subprocess
import dateutil.parser

from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.instance import Kentauros, err, log, log_command

from kentauros.source.source import Source


LOGPREFIX1 = "ktr/source/git: "
"""This string specifies the prefix for log and error messages printed to
``stdout`` or ``stderr`` from inside this subpackage.
"""


class GitSource(Source):
    """
    This Source subclass holds information and methods for handling git sources.

    - If the ``git`` command is not found on the system, ``self.active`` is
      automatically set to ``False``.
    - For the purpose of checking connectivity to the remote server, the URL is
      stored in ``self.remote``.
    - If neither ``branch`` nor ``commit`` hash has been set in the package
      configuration file, then the branch defaults to ``master`` (this is also
      written to the configuration file).
    - If a specific commit hash has been specified in the package configuration
      file, ``shallow`` is automatically set to ``False`` (this is also written
      to the configuration file).

    Arguments:
        Package package:  package instance this :py:class:`GitSource` belongs to
    """

    def __init__(self, package):
        super().__init__(package)
        self.dest = os.path.join(self.sdir, self.name)
        self.type = SourceType.GIT

        # if git is not installed: mark GitSource instance as inactive
        try:
            self.active = True
            subprocess.check_output(["which", "git"])
        except subprocess.CalledProcessError:
            log(LOGPREFIX1 + "Install git to use the specified source.")
            self.active = False

        # either branch or commit must be set. default to branch=master
        if self.conf.get("git", "branch") == "" and \
           self.conf.get("git", "commit") == "":
            self.conf.set("git", "branch", "master")
            self.package.update_config()

        # shallow clones and checking out a specific commit is not supported
        if self.conf.get("git", "commit") != "" and \
           self.conf.getboolean("git", "shallow"):

            self.conf.set("git", "shallow", "false")
            self.package.update_config()

        self.saved_rev = None
        self.saved_date = None


    def date(self) -> str:
        """
        This method provides an easy way of getting the date and time of the
        requrested commit in a standardised format (``YYMMDD.HHmmSS``). It also
        stores the latest parsed date between method invocations, if the source
        goes away and the commit datetime string is needed again.

        Returns:
            str:        commit date.time string (``YYMMDD.HHmmSS``)
        """

        if not self.active:
            return None

        def prepend_zero(string):
            "This local function prepends '0' to one-digit time value strings."
            if len(string) == 1:
                return "0" + string
            else:
                return string

        cmd = ["git", "show", "-s", "--date=short", "--format=%cI"]

        prevdir = os.getcwd()

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_date is None:
                err("Sources need to be get before their age can be read.")
                return None
            else:
                return self.saved_date

        os.chdir(self.dest)
        log_command(LOGPREFIX1, "git", cmd, 0)
        date_raw = subprocess.check_output(cmd).decode().rstrip('\r\n')
        os.chdir(prevdir)

        dateobj = dateutil.parser.parse(date_raw)

        year_str = str(dateobj.year)[2:]
        month_str = prepend_zero(str(dateobj.month))
        day_str = prepend_zero(str(dateobj.day))

        hour_str = prepend_zero(str(dateobj.hour))
        minute_str = prepend_zero(str(dateobj.minute))
        second_str = prepend_zero(str(dateobj.second))

        date = year_str + month_str + day_str + "." + \
            hour_str + minute_str + second_str

        self.saved_date = date
        return date


    def rev(self) -> str:
        """
        This method provides an easy way of getting the commit hash of the
        requrested commit. It also stores the latest commit hash between method
        invocations, if the source goes away and the hash is needed again.

        Returns:
            str:        commit hash
        """

        if not self.active:
            return None

        cmd = ["git", "rev-parse", "HEAD"]

        prevdir = os.getcwd()

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_rev is None:
                err("Sources need to be get before commit hash can be read.")
                return None
            else:
                return self.saved_rev

        os.chdir(self.dest)
        log_command(LOGPREFIX1, "git", cmd, 0)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")
        os.chdir(prevdir)

        self.saved_rev = rev
        return rev


    def formatver(self) -> str:
        """
        This method assembles a standardised version string for git sources.
        This includes the package source base version, the git commit date and
        time and the first eight characters of the git commit hash, for example:
        ``11.3.0~devel~git160422~39e9cf6c``

        Returns:
            str:        nicely formatted version string
        """

        if not self.active:
            return ""

        # base version
        ver = self.conf.get("source", "version")

        # date and time of commit
        ver += "~git"
        ver += self.date()

        # first 8 chars of git commit ID
        ver += "~"
        ver += self.rev()[0:8]

        return ver


    def get(self) -> bool:
        """
        This method executes the git repository download to the package source
        directory. This respects the branch and commit set in the package
        configuration file.

        Returns:
            bool: ``True`` if successful, ``False`` if not or source pre-exists
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
            log(LOGPREFIX1 + "Sources already downloaded. Latest commit id:", 2)
            log(LOGPREFIX1 + rev, 2)
            return False

        # check for connectivity to server
        if not is_connected(self.conf.get("source", "orig")):
            log("No connection to remote host detected. " +
                "Cancelling source checkout.", 2)
            return False

        # construct git commands
        cmd = ["git"]

        # construct clone command
        cmd1 = cmd.copy()
        cmd1.append("clone")

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd1.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd1.append("--verbose")

        # set --depth==1 if shallow is specified
        if self.conf.getboolean("git", "shallow"):
            cmd1.append("--depth=1")

        # set branch if specified
        if self.conf.get("git", "branch"):
            cmd1.append("--branch")
            cmd1.append(self.conf.get("git", "branch"))

        # set origin and destination
        cmd1.append(self.conf.get("source", "orig"))
        cmd1.append(self.dest)

        # clone git repo from orig to dest
        log_command(LOGPREFIX1, "git", cmd1, 0)
        subprocess.call(cmd1)

        # if commit is specified: checkout commit
        if self.conf.get("git", "commit"):
            # construct checkout command
            cmd2 = cmd.copy()
            cmd2.append("checkout")
            cmd2.append(self.conf.get("git", "commit"))

            # go to git repo and remember old cwd
            prevdir = os.getcwd()
            os.chdir(self.dest)

            # checkout commit
            log_command(LOGPREFIX1, "git", cmd2, 0)
            subprocess.call(cmd2)

            # go to previous dir
            os.chdir(prevdir)

        # get commit ID
        rev = self.rev()
        self.date()

        # check if checkout worked
        if self.conf.get("git", "commit"):
            if self.conf.get("git", "commit") != rev:
                err(LOGPREFIX1 + \
                    "Something went wrong, requested commit not in repo.")
                return False

        # return True if successful
        return True


    def update(self) -> bool:
        """
        This method executes a git repository update as specified in the package
        configuration file. If a specific commit has been set in the config
        file, this method will not attempt to execute an update.

        Returns:
            bool: ``True`` if update available and successful, ``False`` if not
        """

        if not self.active:
            return False

        ktr = Kentauros()

        # if specific commit is requested, do not pull updates (obviously)
        if self.conf.get("git", "commit"):
            return False

        # check for connectivity to server
        if not is_connected(self.conf.get("source", "orig")):
            log("No connection to remote host detected. " + \
                "Cancelling source update.", 2)
            return False

        # construct git command
        cmd = ["git"]

        cmd.append("pull")
        cmd.append("--rebase")

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 2) and not ktr.debug:
            cmd.append("--quiet")
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            err(LOGPREFIX1 +
                "Sources need to be get before an update can be run.")
            return False

        # get old commit ID
        rev_old = self.rev()

        # change to git repodir
        prevdir = os.getcwd()
        os.chdir(self.dest)

        # get updates
        log_command(LOGPREFIX1, "git", cmd, 0)
        subprocess.call(cmd)

        # go back to previous dir
        os.chdir(prevdir)

        # get new commit ID
        rev_new = self.rev()
        self.date()

        # return True if update found, False if not
        return rev_new != rev_old


    def export(self) -> bool:
        """
        This method executes the export from the package source repository to a
        tarball with pretty file name. It also respects the ``git.keep=False``
        setting in the package configuration file - the git repository will be
        deleted from disk after the export if this flag is set.

        Returns:
            bool:   ``True`` if successful or already done, ``False`` at failure
        """

        if not self.active:
            return False

        ktr = Kentauros()

        def remove_notkeep():
            """
            This local function removes the git repository after it has been
            exported to a tarball, if ``git.keep=false`` is set.
            """

            if not self.conf.getboolean("git", "keep"):
                # try to be careful with "rm -r"
                assert os.path.isabs(self.dest)
                assert ktr.conf.datadir in self.dest
                shutil.rmtree(self.dest)
                log(LOGPREFIX1 +
                    "git repository has been deleted " +
                    "after exporting to tarball.", 1)

        # construct git command
        cmd = ["git"]

        cmd.append("archive")

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.conf.get("git", "commit") == "":
            cmd.append("HEAD")
        else:
            cmd.append(self.conf.get("git", "commit"))

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            err(LOGPREFIX1 + \
                "Sources need to be get before they can be exported.")
            return False

        version = self.formatver()
        name_version = self.name + "-" + version

        # add prefix
        cmd.append("--prefix=" + name_version + "/")

        file_name = os.path.join(ktr.conf.datadir,
                                 self.name,
                                 name_version + ".tar.gz")

        cmd.append("--output")
        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            log(LOGPREFIX1 + "Tarball has already been exported.", 1)
            # remove git repo if keep is False
            remove_notkeep()
            return True

        # remember previous directory
        prevdir = os.getcwd()

        # change to git repodir
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        log_command(LOGPREFIX1, "git", cmd, 0)
        subprocess.call(cmd)

        # update saved rev and date
        self.rev()
        self.date()

        # remove git repo if keep is False
        remove_notkeep()

        os.chdir(prevdir)
        return True

