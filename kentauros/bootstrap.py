import os

from .context import KtrContext
from .result import KtrResult


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


def ktr_bootstrap(context: KtrContext) -> KtrResult:
    ret = KtrResult(name="bootstrap")

    for path in [context.get_basedir(), context.get_confdir(), context.get_datadir(),
                 context.get_expodir(), context.get_packdir(), context.get_specdir()]:

        res = ktr_mkdirp(path)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

    return ret.submit(True)
