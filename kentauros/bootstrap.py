"""
This module contains functions that cover the bare necessity of setting up the directories kentauros
expects to exist. This happens after CLI arguments and environment variables have been parsed to
determine which directories those should be.
"""

import os

from .context import KtrContext
from .logcollector import LogCollector


def ktr_mkdirp(path: str, logger: LogCollector) -> bool:
    """
    This function checks for directory existence and the ability to write to it. If the directory
    does not exist, it will be created.

    Arguments:
        str path:   path of directory to check and create

    Returns:
        bool:       success (or not)
    """

    if os.path.exists(path):
        if os.access(path, os.W_OK):
            return True
        else:
            logger.err(path + " can't be written to.")
            return False
    else:
        logger.log(path + " directory doesn't exist and will be created.")
        try:
            os.makedirs(path)
        except OSError:
            logger.err(path + " directory could not be created.")
            return False
        return True


def ktr_bootstrap(context: KtrContext, logger: LogCollector) -> bool:
    """
    This function has to be called before any other actions are attempted on packages. It ensures
    that the required directory structure is present. If it fails, kentauros execution will be
    aborted.

    Returns:
        bool:       success (or not)
    """

    for path in [context.get_basedir(), context.get_confdir(), context.get_datadir(),
                 context.get_expodir(), context.get_packdir(), context.get_specdir()]:
        if not ktr_mkdirp(path, logger):
            return False

    return True
