"""
kentauros.bootstrap module
after ENV variables, CLI switches and config files have been evaluated:
bootstrap kentauros for actual use
"""

import os

from kentauros.config import KTR_CONF
from kentauros.init import log


def ktr_create_dirs():
    """
    kentauros.bootstrap.ktr_create_dirs()
    create confdir, datadir, specdir specified by ENV, CLI, configuration files
    """
    if not os.access(KTR_CONF.confdir, os.W_OK):
        log("kentauros confdir does not exist and will be created.", 1)
        os.makedirs(KTR_CONF.confdir)

    if not os.access(KTR_CONF.datadir, os.W_OK):
        log("kentauros datadir does not exist and will be created.", 1)
        os.makedirs(KTR_CONF.datadir)

    if not os.access(KTR_CONF.specdir, os.W_OK):
        log("kentauros specdir does not exist and will be created.", 1)
        os.makedirs(KTR_CONF.specdir)


def ktr_bootstrap():
    """
    kentauros.bootstrap.ktr_bootstrap()
    bootstrap everything for actual use of ktr
    """
    ktr_create_dirs()

