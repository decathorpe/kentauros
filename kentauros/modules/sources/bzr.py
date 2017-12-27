"""
This sub-module only contains the :py:class:`BzrSource` class, which has methods for handling
sources that have `source.type=bzr` specified and `source.orig` set to a bzr repository URL (or an
`lp:` abbreviation) in the package's configuration file.
"""

import configparser as cp
import datetime
import os
import shutil

from ...conntest import is_connected
from ...context import KtrContext
from ...logcollector import LogCollector
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand
from ...validator import KtrValidator

from .abstract import Source


class BzrCommand(ShellCommand):
    NAME = "Bzr Command"

    def __init__(self, path: str, *args, bzr=None):
        if bzr is None:
            self.exec = "bzr"
        else:
            self.exec = bzr

        super().__init__(path, self.exec, *args)


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

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.dest = os.path.join(self.sdir, self.package.name)
        self.stype = "bzr"
        self.saved_date = None
        self.saved_rev = None

        orig = self.get_orig()

        if orig[0:3] == "lp:":
            self.remote = "https://launchpad.net"
        else:
            self.remote = orig

    def __str__(self) -> str:
        return "bzr Source for Package '" + self.package.conf_name + "'"

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

        # check if the configuration file is valid
        expected_keys = ["branch", "keep", "keep_repo", "orig", "revno"]
        expected_binaries = ["bzr"]

        validator = KtrValidator(self.package.conf.conf, "bzr", expected_keys, expected_binaries)

        return validator.validate()

    def get_keep(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the exported tarball should be kept
        """

        return self.package.conf.getboolean("bzr", "keep")

    def get_keep_repo(self) -> bool:
        """
        Returns:
            bool:   boolean value indicating whether the bzr repository should be kept
        """

        return self.package.conf.getboolean("bzr", "keep_repo")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the upstream bzr repository URL (or `lp:` link)
        """

        return self.package.replace_vars(self.package.conf.get("bzr", "orig"))

    def get_branch(self) -> str:
        """
        Returns:
            str:    string containing the branch that is set in the package configuration
        """

        return self.package.conf.get("bzr", "branch")

    def get_revno(self) -> str:
        """
        Returns:
            str:    string containing the revision number that is set in the package configuration
        """

        return self.package.conf.get("bzr", "revno")

    def rev(self) -> KtrResult:
        """
        This method determines which revision the bzr repository associated with this
        :py:class:`BzrSource` currently is at and returns it as a string. Once run, it saves the
        last processed revision number in `self.saved_rev`, in case the revision needs to be
        determined when bzr repository might not be accessible anymore (e.g. if `bzr.keep=False` is
        set in configuration, so the repository is not kept after export to tarball).

        Returns:
            str: either revision string from repo, last stored rev string or `""` when unsuccessful
        """

        ret = KtrResult(name=self.name())

        if not os.access(self.dest, os.R_OK):
            state = self.context.state.read(self.package.conf_name)

            if self.saved_rev is not None:
                ret.value = self.saved_rev
                return ret.submit(True)
            elif state is not None:
                if "bzr_last_rev" in state:
                    ret.value = state["bzr_last_rev"]
                    return ret.submit(True)
            else:
                ret.messages.err("Sources must be present to determine the revision.")
                return ret.submit(False)

        res = BzrCommand(self.dest, "revno").execute()
        ret.collect(res)

        if res.success:
            self.saved_rev = res.value
            ret.value = res.value
            ret.state["bzr_last_rev"] = res.value
            return ret.submit(True)
        else:
            ret.messages.log("Bzr command to determine revision number unsuccessful.")
            return ret.submit(False)

    def datetime(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = BzrCommand(self.dest, "version-info").execute()

        if not res.success:
            ret.messages.log("Bzr command did not execute successfully. No revision date obtained.")
            ret.messages.err("Assuming 'now' as fallback date/time.")
            ret.value = datetime.datetime.now().astimezone(datetime.timezone.utc)
            return ret.submit(False)

        for line in res.value:
            if line[0:6] == "date: ":
                date_string = line.replace("date: ", "")

                ret.value = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")
                return ret.submit(True)

        ret.messages.err("No date information present in the output of 'bzr version-info'.")
        ret.messages.err("Assuming 'now' as fallback date/time.")

        ret.value = datetime.datetime.now()
        return ret.submit(False)

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
        ret.state["bzr_last_date"] = string

        return ret.submit(res.success)

    def date(self) -> KtrResult:
        res = self.datetime()
        dt = res.value

        return KtrResult(res.success, "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day))

    def time(self) -> KtrResult:
        res = self.datetime()
        dt = res.value

        return KtrResult(res.success, "{:02d}{:02d}{:02d}".format(dt.hour, dt.minute, dt.second))

    def status(self) -> KtrResult:
        """
        This method returns statistics describing this BzrSource object and its associated file(s).
        At the moment, this only includes the branch and revision specified in the configuration
        file.

        Returns:
            dict:   key-value pairs (property: value)
        """

        ret = KtrResult(name=self.name())

        dt = self.datetime_str()
        ret.collect(dt)

        rev = self.rev()
        ret.collect(rev)

        version_format = self.formatver()
        ret.collect(version_format)

        ret.state["bzr_branch"] = self.get_branch()
        ret.state["bzr_rev"] = self.get_revno()

        success = dt.success and rev.success and version_format.success
        return ret.submit(success)

    def status_string(self) -> KtrResult:
        template = """
        bzr source module:
          Last Revision:    {rev}
          Current Branch:   {branch}
        """

        res = self.rev()

        if not res.success:
            string = template.format(rev="Unavailable", branch=self.get_branch())
        else:
            rev = res.value
            string = template.format(rev=rev, branch=self.get_branch())

        return KtrResult(res.success, string)

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            # Sources have already been downloaded, stats can be got as usual
            return self.status()
        else:
            # Sources aren't there, last rev can't be determined
            return KtrResult(True, state=dict(bzr_branch=self.get_branch(),
                                              bzr_rev=self.get_revno()))

    def formatver(self) -> KtrResult:
        """
        This method returns a nicely formatted version string for bzr sources.

        Returns:
            str: nice version string (base version + "+bzr" + revision)
        """

        ret = KtrResult(name=self.name())
        success = True

        fallback_template = "%{version}%{version_sep}%{date}.%{time}.bzr%{revision}"

        try:
            template: str = self.context.conf.get("main", "version_template_bzr")
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

        if "%{revision}" in template:
            res = self.rev()
            ret.collect(res)

            if res.success:
                template = template.replace("%{revision}", res.value)
            else:
                success = False

        if "%{" in template:
            ret.messages.log("Unrecognized variables present in bzr version template.")
            success = False

        ret.value = template
        ret.state["version_format"] = template
        return ret.submit(success)

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

        ret = KtrResult(name=self.name())

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            res = self.rev()
            ret.collect(res)

            if res.success:
                ret.messages.log("Sources already downloaded. Latest revision: " + res.value)
                return ret.submit(False)

        # check for connectivity to server
        if not is_connected(self.remote):
            ret.messages.log("No connection to remote host detected. Cancelling source checkout.")
            return ret.submit(False)

        # construct bzr command
        cmd = ["branch"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

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
        res = BzrCommand(".", *cmd).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Sources could not be branched successfully.")
            return ret.submit(False)

        # get commit ID
        res = self.rev()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Revision could not be determined successfully.")
            return ret.submit(False)

        # check if checkout worked
        if self.get_revno():
            if self.get_revno() != res.value:
                ret.messages.err("Something went wrong, requested commit not available.")
                return ret.submit(False)

        # return True if successful
        ret.collect(self.status())
        return ret.submit(True)

    def update(self) -> KtrResult:
        """
        This method executes a bzr repository update as specified in the package configuration file.
        If a specific revision has been set in the config file, this method will not attempt to
        execute an update.

        Returns:
            bool: `True` if update available and successful, `False` otherwise
        """

        ret = KtrResult(name=self.name())

        # if specific revision is requested, do not pull updates (obviously)
        if self.get_revno():
            return ret.submit(False)

        # check for connectivity to server
        if not is_connected(self.remote):
            ret.messages.log("No connection to remote host detected. Cancelling source checkout.")
            return ret.submit(False)

        # construct bzr command
        cmd = ["pull"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        # check if source directory exists before going there
        if not os.access(self.dest, os.W_OK):
            ret.messages.err("Sources need to be .get() before .update() can be run.")
            return ret.submit(False)

        # get old revision number
        res = self.rev()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Revision could not be determined successfully.")
            return ret.submit(False)
        rev_old = res.value

        # run pull command
        res = BzrCommand(self.dest, *cmd).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Sources could not be updated successfully.")
            return ret.submit(False)

        # get new commit ID
        res = self.rev()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Revision could not be determined successfully.")
            return ret.submit(False)
        rev_new = res.value

        # return True if update found, False if not
        updated = rev_new != rev_old

        ret.collect(self.status())
        return ret.submit(updated)

    def _remove_or_keep(self, logger: LogCollector):
        """
        This private method removes the bzr repository and is called after source export, if
        not keeping the repository around was specified in the configuration file.
        """

        if not self.get_keep_repo():
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert self.context.get_datadir() in self.dest

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

        ret = KtrResult(name=self.name())

        # construct bzr command
        cmd = ["export"]

        # add --verbose or --quiet depending on settings
        if self.context.debug():
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        # export HEAD or specified commit
        if self.get_revno():
            cmd.append("--revision")
            cmd.append(self.get_revno())

        # check if bzr repo exists
        if not os.access(self.dest, os.R_OK):
            ret.messages.err("Sources need to be get before they can be exported.")
            return ret.submit(False)

        res = self.formatver()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Version could not be formatted successfully.")
            return ret.submit(False)
        version = res.value

        name_version = self.package.name + "-" + version
        file_name = name_version + ".tar.gz"
        file_path = os.path.join(self.sdir, file_name)

        cmd.append(file_path)

        # check if file has already been exported
        if os.path.exists(file_path):
            ret.messages.log("Tarball has already been exported.")
            # remove bzr repo if keep is False
            self._remove_or_keep(ret.messages)
            return ret.submit(True)

        res = BzrCommand(self.dest, *cmd).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.err("bzr command could not be executed successfully.")
            return ret.submit(False)

        # update saved rev
        res = self.rev()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Revision could not be determined successfully.")
            return ret.submit(False)

        # remove bzr repo if keep is False
        self._remove_or_keep(ret.messages)

        ret.collect(self.status())
        ret.state["source_files"] = [file_name]
        return ret.submit(True)
