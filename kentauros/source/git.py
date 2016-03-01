"""
kentauros.source.git
contains GitSource class and methods
this class is for handling sources that are specified by git repo URL
"""

import dateutil.parser
from distutils.util import strtobool
import os
import shutil
import subprocess

from kentauros.config import KTR_CONF
from kentauros.conntest import is_connected
from kentauros.definitions import SourceType
from kentauros.init import DEBUG, VERBY, err, log, log_command
from kentauros.source.common import Source


LOGPREFIX1 = "ktr/source/git: "


class GitSource(Source):
    """
    kentauros.source.GitSource
    information about and methods for git repositories available at specified URL
    this defaults to:
    - full checkout of source
    - keeping sources between transactions
    - checking out master branch
    """

    def __init__(self, pkgconfig):
        super().__init__(pkgconfig)
        self.config = pkgconfig
        self.dest = os.path.join(self.sdir, self.name)
        self.type = SourceType.GIT

        # either branch or commit must be set. default to branch=master
        if self.conf.get("git", "branch") == "" and self.conf.get("git", "commit") == "":
            self.conf.set("git", "branch", "master")
            self.package.update_config()

        # shallow clones and checking out a specific commit is not supported
        if self.conf.get("git", "commit") != "" and \
            bool(strtobool(self.conf.get("git", "shallow"))):

            self.conf.set("git", "shallow", "false")
            self.package.update_config()

        self.saved_rev = None
        self.saved_date = None


    def date(self):
        """
        kentauros.source.git.GitSource.date()
        returns date of HEAD commit
        """

        cmd = ["git", "show", "-s", "--date=short", "--format=%cI"]

        prevdir = os.getcwd()

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_date == None:
                err("Sources need to be .get() before .date() can be determined.")
                return None
            else:
                return self.saved_date

        os.chdir(self.dest)
        log_command(LOGPREFIX1, "git", cmd, 0)
        date_raw = subprocess.check_output(cmd).decode().rstrip('\r\n')
        os.chdir(prevdir)

        # pylint: disable=no-member
        dateobj = dateutil.parser.parse(date_raw)
        date = str(dateobj.year) + str(dateobj.month) + str(dateobj.day) + \
               "." + \
               str(dateobj.hour) + str(dateobj.minute) + str(dateobj.second)

        self.saved_date = date
        return date


    def rev(self):
        """
        kentauros.source.git.GitSource.rev()
        returns commit id of repository
        """

        cmd = ["git", "rev-parse", "HEAD"]

        prevdir = os.getcwd()

        # if sources are not accessible (anymore), return None or last saved rev
        if not os.access(self.dest, os.R_OK):
            if self.saved_rev == None:
                err("Sources need to be .get() before .rev() can be determined.")
                return None
            else:
                return self.saved_rev

        os.chdir(self.dest)
        log_command(LOGPREFIX1, "git", cmd, 0)
        rev = subprocess.check_output(cmd).decode().rstrip("\n")
        os.chdir(prevdir)

        self.saved_rev = rev
        return rev


    def formatver(self):
        ver = self.conf.get("source", "version")    # base version
        ver += "~git"
        ver += self.date()                          # date and time of commit
        ver += "~"
        ver += self.rev()[0:8]                      # first 8 chars of git commit ID
        return ver


    def get(self):
        """
        kentauros.source.git.GitSource.get()
        get sources from specified branch at orig
        returns commit id of latest commit
        """

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source directory seems to already exist, quit and return commit id
        if os.access(self.dest, os.R_OK):
            rev = self.rev()
            log(LOGPREFIX1 + "Sources already downloaded. Latest commit id:", 2)
            log(LOGPREFIX1 + rev, 2)
            return rev

        # check for connectivity to server
        if not is_connected(self.config.get("source", "orig")):
            log("No connection to remote host detected. Cancelling source checkout.", 2)
            return None

        # construct git commands
        cmd = ["git"]

        # construct clone command
        cmd1 = cmd
        cmd1.append("clone")

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd1.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd1.append("--verbose")

        # set --depth==1 if shallow is specified
        if bool(strtobool(self.conf.get("git", "shallow"))):
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
            cmd2 = cmd
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

        # check if checkout worked
        if self.conf.get("git", "commit"):
            if self.conf.get("git", "commit") != rev:
                err(LOGPREFIX1 + "Something went wrong, requested commit is not commit in repo.")

        # return commit ID
        return rev


    def update(self):
        """
        kentauros.source.git.GitSource.update()
        update sources to latest commit in specified branch
        returns True if update happened, False if not
        """

        # if specific commit is requested, do not pull updates (obviously)
        if self.conf.get("git", "commit"):
            return False

        # check for connectivity to server
        if not is_connected(self.config.get("source", "orig")):
            log("No connection to remote host detected. Cancelling source update.", 2)
            return False

        # construct git command
        cmd = ["git"]

        cmd.append("pull")
        cmd.append("--rebase")

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            err(LOGPREFIX1 + "Sources need to be .get() before .update() can be run.")
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

        # return True if update found, False if not
        if rev_new != rev_old:
            return True
        else:
            return False


    def export(self):
        """
        kentauros.source.git.GitSource.export()
        exports current git commit to tarball (.tar.gz)
        """

        # construct git command
        cmd = ["git"]

        cmd.append("archive")

        # add --verbose or --quiet depending on settings
        if (VERBY == 2) and not DEBUG:
            cmd.append("--quiet")
        if (VERBY == 0) or DEBUG:
            cmd.append("--verbose")

        # export HEAD or specified commit
        if self.conf.get("git", "commit") == "":
            cmd.append("HEAD")
        else:
            cmd.append(self.conf.get("git", "commit"))

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            err(LOGPREFIX1 + "Sources need to be .get() before they can be .export()ed.")
            return None

        version = self.formatver()
        name_version = self.name + "-" + version

        # add prefix
        cmd.append("--prefix=" + name_version + "/")

        file_name = os.path.join(KTR_CONF['main']['datadir'],
                                 self.name,
                                 name_version + ".tar.gz")

        cmd.append("--output")
        cmd.append(file_name)

        # check if file has already been exported
        if os.path.exists(file_name):
            log(LOGPREFIX1 + "Tarball has already been exported.", 1)
            return False

        # remember previous directory
        prevdir = os.getcwd()

        # change to git repodir
        os.chdir(self.dest)

        # export tar.gz to $KTR_DATA_DIR/$PACKAGE/*.tar.gz
        log_command(LOGPREFIX1, "git", cmd, 0)
        subprocess.call(cmd)

        # remove git repo if keep is False
        if not bool(strtobool(self.conf.get("git", "keep"))):
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert KTR_CONF['main']['datadir'] in self.dest
            shutil.rmtree(self.dest)
            log(LOGPREFIX1 + "git repo deleted after export to tarball", 1)

        os.chdir(prevdir)
        return True

