import configparser as cp
import os

from kentauros.context import KtrContext
from kentauros.result import KtrResult
from kentauros.templates import KENTAUROSRC_TEMPLATE
from .meta import KtrMetaTask


def ktr_mkdirp(path: str) -> KtrResult:
    ret = KtrResult(name="bootstrap")

    if os.path.exists(path):
        if os.access(path, os.W_OK):
            return ret.submit(True)
        else:
            ret.messages.err(path + " can't be written to.")
            return ret.submit(False)
    else:
        ret.messages.log(path + " directory doesn't exist and will be created.")
        try:
            os.makedirs(path)
        except OSError:
            ret.messages.err(path + " directory could not be created.")
            return ret.submit(False)
        return ret.submit(True)


class KtrInitTask(KtrMetaTask):
    def __init__(self, context: KtrContext):
        self.context = context

    def execute(self) -> KtrResult:
        ret = KtrResult(True, name="bootstrap")

        try:
            basedir = self.context.get_basedir()
            path = os.path.join(basedir, "kentaurosrc")

            with open(path, "a") as file:
                file.write(KENTAUROSRC_TEMPLATE)

            conf = cp.ConfigParser()
            conf.read(path)

            if basedir == os.getcwd():
                basedir_conf = "./"
            else:
                basedir_conf = basedir

            conf.set("main", "basedir", basedir_conf)

            with open(path, "w") as file:
                conf.write(file)
        except OSError:
            ret.messages.log("kentaurosrc file could not be created.")
            ret.success = False

        for path in [self.context.get_basedir(), self.context.get_confdir(),
                     self.context.get_datadir(), self.context.get_expodir(),
                     self.context.get_packdir(), self.context.get_specdir()]:

            res = ktr_mkdirp(path)
            ret.collect(res)

            if not res.success:
                return ret

        return ret
