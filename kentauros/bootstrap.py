"""
This module contains functions that cover the bare necessity of setting up the directories kentauros
expects to exist. This happens after CLI arguments and environment variables have been parsed to
determine which directories those should be.
"""


import os

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger


LOG_PREFIX = "ktr/bootstrap"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


def ktr_mkdirp(path: str) -> bool:
    """
    This function checks for directory existence and the ability to write to it. If the directory
    does not exist, it will be created.

    Arguments:
        str path:   path of directory to check and create

    Returns:
        bool:       success (or not)
    """

    logger = KtrLogger(LOG_PREFIX)

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


def ktr_bootstrap() -> bool:
    """
    This function has to be called before any other actions are attempted on packages. It ensures
    that the required directory structure is present. If it fails, kentauros execution will be
    aborted.

    Returns:
        bool:       success (or not)
    """

    ktr = Kentauros()

    for path in [ktr.conf.get_basedir(), ktr.conf.get_confdir(), ktr.conf.get_datadir(),
                 ktr.conf.get_expodir(), ktr.conf.get_packdir(), ktr.conf.get_specdir()]:
        if not ktr_mkdirp(path):
            return False

    return True
