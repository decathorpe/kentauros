"""
This module contains functions that cover the bare necessity of setting up the directories kentauros
expects to exist. This happens after CLI arguments and environment variables have been parsed to
determine which directories those should be.
"""

import os

from .context import KtrContext
from .result import KtrResult


def ktr_mkdirp(path: str) -> KtrResult:
    """
    This function checks for directory existence and the ability to write to it. If the directory
    does not exist, it will be created.

    Arguments:
        str path:   path of directory to check and create

    Returns:
        bool:       success (or not)
    """

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
    """
    This function has to be called before any other actions are attempted on packages. It ensures
    that the required directory structure is present. If it fails, kentauros execution will be
    aborted.

    Returns:
        bool:       success (or not)
    """

    ret = KtrResult(name="bootstrap")

    for path in [context.get_basedir(), context.get_confdir(), context.get_datadir(),
                 context.get_expodir(), context.get_packdir(), context.get_specdir()]:

        res = ktr_mkdirp(path)
        ret.collect(res)

        if not res.success:
            return ret.submit(False)

    return ret.submit(True)
