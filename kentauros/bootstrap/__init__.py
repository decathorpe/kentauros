"""
kentauros.bootstrap module
after ENV variables, CLI switches and config files have been evaluated:
bootstrap kentauros for actual use
"""

import os

from kentauros.instance import Kentauros, log


LOGPREFIX = "ktr/bootstrap: "


def ktr_create_dirs():
    """
    kentauros.bootstrap.ktr_create_dirs()
    create confdir, datadir, specdir specified by ENV, CLI, configuration files
    """

    ktr = Kentauros()

    if not os.access(ktr.conf.basedir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros basedir does not exist and will be created.", 1)
        os.makedirs(ktr.conf.basedir)

    if not os.access(ktr.conf.confdir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros confdir does not exist and will be created.", 1)
        os.makedirs(ktr.conf.confdir)

    if not os.access(ktr.conf.datadir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros datadir does not exist and will be created.", 1)
        os.makedirs(ktr.conf.datadir)

    if not os.access(ktr.conf.packdir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros packdir does not exist and will be created.", 1)
        os.makedirs(ktr.conf.packdir)

    if not os.access(ktr.conf.specdir, os.W_OK):
        log(LOGPREFIX + \
            "kentauros specdir does not exist and will be created.", 1)
        os.makedirs(ktr.conf.specdir)


def ktr_bootstrap():
    """
    kentauros.bootstrap.ktr_bootstrap()
    bootstrap everything for actual use of ktr
    """
    ktr_create_dirs()

