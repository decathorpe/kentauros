import os

from .meta import KtrMetaTask
from ..context import KtrContext
from ..result import KtrResult


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
        ret = KtrResult(name="bootstrap")

        # TODO: create kentaurosrc file from template

        for path in [self.context.get_basedir(), self.context.get_confdir(),
                     self.context.get_datadir(), self.context.get_expodir(),
                     self.context.get_packdir(), self.context.get_specdir()]:

            res = ktr_mkdirp(path)
            ret.collect(res)

            if not res.success:
                return ret.submit(False)

        return ret.submit(True)
