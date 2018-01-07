import os
import subprocess as sp

from .result import KtrResult


class ShellCmd:
    NAME = "Shell Command"

    def __init__(self, binary: str, path: str = None):
        if path is None:
            self.path = os.getcwd()
        else:
            self.path = path

        self.args = [binary]

    def command(self, *args) -> 'ShellCmd':
        self.args.extend(args)
        return self

    def execute(self, ignore_retcode: bool = False) -> KtrResult:
        ret = KtrResult()

        cwd = os.getcwd()

        try:
            os.chdir(self.path)
            ret.messages.cmd(self.args)
            res: sp.CompletedProcess = sp.run(self.args, stdout=sp.PIPE, stderr=sp.STDOUT)
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
