import datetime

from git import Repo
from git.exc import BadName

from ...result import KtrResult
from ...shellcmd import ShellCommand


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

        res = GitCommand(*cmd).execute()
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

        if not shallow:
            res = GitCommand(".", "clone", "--quiet", orig, path).execute()
        else:
            res = GitCommand(".", "--quiet", "--depth=1", orig, path).execute()

        ret.collect(res)

        if not res.success:
            return ret.submit(False)

        repo = GitRepo(path, ref)
        ret.value = repo
        return ret.submit(True)
