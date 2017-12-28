import os
import subprocess as sp

from .result import KtrResult


class ShellCommand:
    NAME = "Shell Command"

    def __init__(self, path: str, *args):
        self.path = path
        self.args = args

    def execute(self, ignore_retcode: bool = False) -> KtrResult:
        ret = KtrResult()

        cmd = list()
        cmd.extend(self.args)

        cwd = os.getcwd()

        try:
            os.chdir(self.path)
            ret.messages.cmd(cmd)
            res: sp.CompletedProcess = sp.run(cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
        finally:
            os.chdir(cwd)

        out = res.stdout.decode().rstrip("\n")
        ret.value = out

        if (res.returncode == 0) or ignore_retcode:
            return ret.submit(True)
        else:
            ret.messages.err(
                "The command did not quit with return code 0 ({}), indicating an error.".format(
                    res.returncode))
            return ret.submit(False)
