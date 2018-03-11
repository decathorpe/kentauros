import logging
import os
import subprocess as sp

from .result import KtrResult


class ShellCmdException(Exception):
    pass


class ShellEnv:
    def __init__(self, wd: str = None):
        self.cwd = os.getcwd()

        if wd is None:
            self._wd = self.cwd
        else:
            self._wd = os.path.abspath(wd)

    @property
    def wd(self):
        return self._wd

    def __enter__(self):
        if self.wd:
            os.chdir(self.wd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.wd:
            os.chdir(self.cwd)

    def execute(self, *command, ignore_retcode: bool = False) -> KtrResult:
        if os.getcwd() != self.wd:
            raise ShellCmdException("Fatal error: Current directory is not the working directory.")

        ret = KtrResult()

        args = list(command)

        logger = logging.getLogger(f"ktr/{args[0]} command")

        logger.debug(" ".join(args))

        try:
            res: sp.CompletedProcess = sp.run(args, stdout=sp.PIPE, stderr=sp.STDOUT)
        except FileNotFoundError as error:
            return KtrResult(False, value=f"Fatal: {error.filename} command not found.")

        ret.value = res.stdout.decode().rstrip("\n")

        if (res.returncode == 0) or ignore_retcode:
            return ret.submit(True)
        else:
            logger.error(f"This subprocess didn't return 0 ({res.returncode}):")
            logger.error(" ".join(args))
            return ret.submit(False)
