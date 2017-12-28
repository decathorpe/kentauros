import configparser as cp
import datetime
import os
import shutil

from git import Repo
from git.exc import BadName

from .abstract import Source
from ...conntest import is_connected
from ...context import KtrContext
from ...logcollector import LogCollector
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand
from ...validator import KtrValidator


class GitCommand(ShellCommand):
    NAME = "Bzr Command"

    def __init__(self, path: str, *args, binary=None):
        if binary is None:
            self.exec = "git"
        else:
            self.exec = binary

        super().__init__(path, self.exec, *args)


class GitRepo:
    def __init__(self, path: str, ref: str = None):
        assert isinstance(path, str)

        self.path = path
        self.repo = Repo(self.path)

        if ref is None:
            self.ref = "HEAD"
        else:
            self.ref = ref

    def get_commit(self, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = KtrResult()

        try:
            rev = self.repo.rev_parse(ref)
        except BadName as error:
            ret.messages.log(repr(error))
            return ret.submit(False)

        ret.value = rev.hexsha
        return ret.submit(True)

    def get_datetime(self, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = KtrResult()

        res = self.get_commit(ref)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)
        commit = res.value

        try:
            commit_obj = self.repo.commit(commit)
        except BadName as error:
            ret.messages.log(repr(error))
            return ret.submit(False)

        ret.value = commit_obj.committed_datetime.astimezone(datetime.timezone.utc)
        return ret.submit(True)

    def get_datetime_str(self, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = KtrResult()

        res = self.get_datetime(ref)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)
        dt = res.value

        template = "{:04d}{:02d}{:02d} {:02d}{:02d}{:02d}"
        ret.value = template.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        return ret.submit(True)

    def get_date(self, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = KtrResult()

        res = self.get_datetime(ref)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)
        dt = res.value

        template = "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)
        ret.value = template.format(dt.year, dt.month, dt.day)
        return ret.submit(True)

    def get_time(self, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = KtrResult()

        res = self.get_datetime(ref)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)
        dt = res.value

        template = "{:02d}{:02d}{:02d}"
        ret.value = template.format(dt.hour, dt.minute, dt.second)
        return ret.submit(True)

    def checkout(self, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = GitCommand(self.path, "checkout", ref).execute()
        return ret

    def pull(self, rebase: bool = True, all_branches: bool = True, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = KtrResult()

        cmd = [self.path, "pull"]

        if rebase:
            cmd.append("--rebase")

        if all_branches:
            cmd.append("--all")

        res = GitCommand(self.path, *cmd).execute()
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        res = self.checkout(ref)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        return ret.submit(True)

    def export(self, prefix: str, path: str, ref: str = None) -> KtrResult:
        if ref is None:
            ref = self.ref
        assert isinstance(ref, str)

        ret = GitCommand(self.path, "archive", ref, "--prefix=" + prefix,
                         "--output", path).execute()
        return ret

    @staticmethod
    def clone(path: str, orig: str, ref: str = None, shallow: bool = False) -> KtrResult:
        assert isinstance(path, str)
        assert isinstance(orig, str)
        assert isinstance(ref, str)

        ret = KtrResult()

        # clone the repository
        if not shallow:
            res = GitCommand(".", "clone", orig, path).execute()
        else:
            res = GitCommand(".", "clone", "--depth=1", orig, path).execute()

        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        repo = GitRepo(path, ref)

        # check out the specified ref
        res = repo.checkout(ref)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        ret.value = repo
        return ret.submit(True)


FALLBACK_TEMPLATE = "%{version}%{version_sep}%{date}.%{time}.git%{shortcommit}"


class GitSource(Source):
    NAME = "git Source"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.dest = os.path.join(self.sdir, self.package.name)
        self.stype = "git"

        self.saved_date: datetime.datetime = None
        self.saved_commit: str = None

    def __str__(self) -> str:
        return "git Source for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        expected_keys = ["keep", "keep_repo", "orig", "ref", "shallow"]
        expected_binaries = ["git"]

        validator = KtrValidator(self.package.conf.conf, "git", expected_keys, expected_binaries)

        ret = validator.validate()

        # shallow clones and checking out a specific commit is not supported
        if (self.get_ref() != "master") and self.get_shallow():
            ret.messages.err(
                "Shallow clones are not compatible with specifying a specific ref.")

            return ret.submit(False)

        return ret

    def get_keep(self) -> bool:
        return self.package.conf.getboolean("git", "keep")

    def get_keep_repo(self) -> bool:
        return self.package.conf.getboolean("git", "keep_repo")

    def get_orig(self) -> str:
        return self.package.replace_vars(self.package.conf.get("git", "orig"))

    def get_ref(self) -> str:
        ref = self.package.conf.get("git", "ref")

        if not ref:
            return "master"
        else:
            return ref

    def _get_commit(self) -> KtrResult:
        repo = GitRepo(self.dest)
        return repo.get_commit(self.get_ref())

    def get_shallow(self) -> bool:
        return self.package.conf.getboolean("git", "shallow")

    def datetime(self) -> KtrResult:
        ret = KtrResult(name=self.name())

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
                        ret.messages.dbg("Saved git commit date not available. Returning 'now'.")
                        dt = datetime.datetime.now()
                    else:
                        dt = datetime.datetime.strptime(saved_dt, "%Y%m%d %H%M%S")
            else:
                ret.messages.err("Sources need to be 'get' before the commit date can be read.")
                ret.messages.err("Falling back to 'now'.")
                dt = datetime.datetime.now().astimezone(datetime.timezone.utc)
        else:
            repo = GitRepo(self.dest)
            dt = repo.get_datetime(self.get_ref())

        self.saved_date = dt

        ret.value = dt
        return ret.submit(True)

    def datetime_str(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.datetime()
        ret.collect(res)

        if not res.success:
            return ret
        dt = res.value

        template = "{:04d}{:02d}{:02d} {:02d}{:02d}{:02d}"
        string = template.format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

        ret.value = string
        ret.state["git_last_date"] = string

        return ret

    def date(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.datetime()
        ret.collect(res)

        if res.success:
            dt = res.value
            ret.value = "{:04d}{:02d}{:02d}".format(dt.year, dt.month, dt.day)

        return ret

    def time(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.datetime()
        ret.collect(res)

        if res.success:
            dt = res.value
            ret.value = "{:02d}{:02d}{:02d}".format(dt.hour, dt.minute, dt.second)

        return ret

    def commit(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if not os.access(self.dest, os.R_OK):
            state = self.context.state.read(self.package.conf_name)

            if self.saved_commit is not None:
                ret.value = self.saved_commit
                return ret

            elif (state is not None) and \
                    ("git_last_commit" in state) and \
                    (state["git_last_commit"] != ""):
                ret.value = state["git_last_commit"]
                return ret

            else:
                ret.messages.err("Sources must be present to determine the revision.")
                return ret.submit(False)

        res = self._get_commit()
        ret.collect(res)

        if not res.success:
            return ret.submit(False)
        commit = res.value

        self.saved_commit = commit

        ret.value = commit
        ret.state["git_last_commit"] = commit
        return ret

    def status(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        dt = self.datetime_str()
        ret.collect(dt)

        commit = self.commit()
        ret.collect(commit)

        version_format = self.formatver()
        ret.collect(version_format)

        ret.state["git_ref"] = self.get_ref()

        return ret

    def status_string(self) -> KtrResult:
        ret = KtrResult(name=self.name())

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
        return ret

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            # Sources have already been downloaded, stats can be got as usual
            return self.status()
        else:
            # Sources aren't there, last commit and date can't be determined
            return KtrResult(True, state=dict(git_ref=self.get_ref()))

    def formatver(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        try:
            template: str = self.context.conf.get("main", "version_template_git")
        except cp.ParsingError:
            template = FALLBACK_TEMPLATE
        except cp.NoSectionError:
            template = FALLBACK_TEMPLATE
        except cp.NoOptionError:
            template = FALLBACK_TEMPLATE

        if "%{version}" in template:
            template = template.replace("%{version}", self.package.get_version())

        if "%{version_sep}" in template:
            template = template.replace("%{version_sep}", self.package.get_version_separator())

        if "%{date}" in template:
            res = self.date()
            ret.collect(res)

            if res.success:
                template = template.replace("%{date}", res.value)

        if "%{time}" in template:
            res = self.time()
            ret.collect(res)

            if res.success:
                template = template.replace("%{time}", res.value)

        # determine commit hash and shortcommit
        res = self.commit()
        ret.collect(res)

        if res.success:
            commit = res.value
        else:
            ret.messages.log("Commit hash string could not be determined successfully.")
            return ret

        if "%{commit}" in template:
            template = template.replace("%{revision}", commit)

        if "%{shortcommit}" in template:
            template = template.replace("%{shortcommit}", commit[0:7])

        # look for variables that are still present
        if "%{" in template:
            ret.messages.log("Unrecognized variables present in git version template.")

        ret.value = template
        ret.state["version_format"] = template
        return ret

    def _checkout(self, ref: str = None) -> KtrResult():
        if ref is None:
            ref = self.get_ref()

        repo = GitRepo(self.dest)
        return repo.checkout(ref)

    def get(self) -> KtrResult:
        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        ret = KtrResult(name=self.name())

        # if source directory seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            res = self.commit()
            ret.collect(res)

            if res.success:
                ret.messages.log("Sources already downloaded. Latest commit id:")
                ret.messages.log(res.value)
                return ret

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            ret.messages.log("No connection to remote host detected. Cancelling source checkout.")
            return ret.submit(False)

        # clone the repository and check out the specified ref
        res = GitRepo.clone(self.dest, self.get_orig(), self.get_ref(), self.get_shallow())
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        # get commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Commit hash could not be determined successfully.")
            return ret

        # get commit date/time
        res = self.date()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Commit date/time not be determined successfully.")
            return ret

        # everything eas successful
        ret.collect(self.status())
        return ret

    def update(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            ret.messages.log("No connection to remote host detected. Cancelling source update.")
            return ret.submit(False)

        # get old commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Commit hash could not be determined successfully.")
            return ret
        rev_old = res.value

        # pull updates
        repo = GitRepo(self.dest)
        res = repo.pull(True, True, self.get_ref())
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        # get new commit ID
        res = self.commit()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Commit hash could not be determined successfully.")
            return ret
        rev_new = res.value

        # get new commit date/time
        res = self.date()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Commit date/time not be determined successfully.")
            return ret

        # return True if update found, False if not
        updated = rev_new != rev_old

        ret.collect(self.status())
        return ret.submit(updated)

    def _remove_not_keep(self, logger: LogCollector):
        if not self.get_keep_repo():
            # try to be careful with "rm -r"
            assert os.path.isabs(self.dest)
            assert self.context.get_datadir() in self.dest
            shutil.rmtree(self.dest)
            logger.log("git repository has been deleted after exporting to tarball.")

    def export(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        # check if git repo exists
        if not os.access(self.dest, os.R_OK):
            ret.messages.err("Sources need to be get before they can be exported.")
            return ret.submit(False)

        # get formatted version string
        res = self.formatver()
        ret.collect(res)

        if not res.success:
            ret.messages.err("Version could not be formatted successfully.")
            return ret
        version = res.value

        # construct prefix, file name, and full absolute file path
        name_version = self.package.name + "-" + version
        prefix = name_version + "/"
        file_name = name_version + ".tar.gz"
        file_path = os.path.join(self.sdir, file_name)

        # check if file has already been exported to the determined file path
        if os.path.exists(file_path):
            ret.messages.log("Tarball has already been exported.")
            # remove git repo if keep is False
            self._remove_not_keep(ret.messages)
            return ret.submit(True)

        # export specified ref of the git repository to the file path
        repo = GitRepo(self.dest)
        res = repo.export(prefix, file_path, self.get_ref())
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        # remove git repo if keep is False
        self._remove_not_keep(ret.messages)

        ret.collect(self.status())
        ret.state["source_files"] = [file_name]
        return ret
