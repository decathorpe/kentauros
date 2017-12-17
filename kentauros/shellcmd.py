import os
import subprocess as sp

from .logcollector import LogCollector
from .result import KtrResult


class ShellCommand:
    NAME = "Shell Command"

    def __init__(self, path: str, *args):
        self.path = path
        self.args = args

    def execute(self) -> KtrResult:
        logger = LogCollector(self.NAME)

        cmd = list()
        cmd.extend(self.args)

        cwd = os.getcwd()
        os.chdir(self.path)

        try:
            logger.cmd(cmd)
            ret: sp.CompletedProcess = sp.run(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
        finally:
            os.chdir(cwd)

        if ret.returncode != 0:
            logger.err("The command did not quit with return code 0 ({}), indicating an error."
                       .format(ret.returncode))
            return KtrResult(False, messages=logger)
        else:
            out = ret.stdout.decode().rstrip("\n")
            return KtrResult(True, out, logger)
