"""
kentauros.bootstrap module
after ENV variables, CLI switches and config files have been evaluated:
bootstrap kentauros for actual use
"""

import os

from kentauros.config import ktr_get_conf
from kentauros.init import log


LOGPREFIX = "ktr/bootstrap: "


def ktr_create_dirs():
    """
    kentauros.bootstrap.ktr_create_dirs()
    create confdir, datadir, specdir specified by ENV, CLI, configuration files
    """

    ktr_conf = ktr_get_conf()

    if not os.access(ktr_conf.basedir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros basedir does not exist and will be created.", 1)
        os.makedirs(ktr_conf.basedir)

    if not os.access(ktr_conf.confdir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros confdir does not exist and will be created.", 1)
        os.makedirs(ktr_conf.confdir)

    if not os.access(ktr_conf.datadir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros datadir does not exist and will be created.", 1)
        os.makedirs(ktr_conf.datadir)

    if not os.access(ktr_conf.packdir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros packdir does not exist and will be created.", 1)
        os.makedirs(ktr_conf.packdir)

    if not os.access(ktr_conf.specdir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros specdir does not exist and will be created.", 1)
        os.makedirs(ktr_conf.specdir)


def ktr_bootstrap():
    """
    kentauros.bootstrap.ktr_bootstrap()
    bootstrap everything for actual use of ktr
    """
    ktr_create_dirs()

