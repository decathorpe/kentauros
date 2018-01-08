import os
import shutil
import tempfile

from .meta_context import KtrContext


TEST_CONF = """# kentaurosrc file for running tests in a temporary directory
[main]
basedir=.

version_template_git = %{version}%{version_sep}%{date}.%{time}.git%{shortcommit}

version_separator_pre = ~
version_separator_post = +
"""


class KtrTestContext(KtrContext):
    def __init__(self, force: bool = False, logfile: str = "", message: str = "",
                 debug: bool = False, warnings: bool = False):

        self.test_dir = tempfile.mkdtemp()
        conf_path = os.path.join(self.test_dir, "kentaurosrc")

        with open(conf_path, "w") as file:
            file.write(TEST_CONF)

        super().__init__(basedir=self.test_dir, conf_path=conf_path)

        self.force = force
        self.logfile = logfile
        self.message = message
        self.debug_flag = debug
        self.warnings_flag = warnings

    def __del__(self):
        assert "/tmp/" in self.test_dir
        shutil.rmtree(self.test_dir)

    def get_force(self) -> bool:
        return self.force

    def get_logfile(self) -> str:
        return self.logfile

    def get_message(self) -> str:
        return self.message

    def debug(self) -> bool:
        return self.debug_flag or os.getenv("KTR_DEBUG", False)

    def warnings(self) -> bool:
        return self.warnings_flag or os.getenv("KTR_WARNINGS", False)

    def get_basedir(self) -> str:
        return self.basedir

    def get_confdir(self) -> str:
        return os.path.join(self.get_basedir(), "configs")

    def get_datadir(self) -> str:
        return os.path.join(self.get_basedir(), "sources")

    def get_expodir(self) -> str:
        return os.path.join(self.get_basedir(), "exports")

    def get_packdir(self) -> str:
        return os.path.join(self.get_basedir(), "packages")

    def get_specdir(self) -> str:
        return os.path.join(self.get_basedir(), "specs")
