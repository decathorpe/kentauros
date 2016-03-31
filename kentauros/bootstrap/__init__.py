"""
This subpackage contains functions that cover the bare necessity of setting up
the directories kentauros expects to exist. This happens after CLI arguments
and environment variables have been parsed to determine which directories those
should be.
"""


import os

from kentauros.instance import Kentauros, log


LOGPREFIX = "ktr/bootstrap: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


def ktr_bootstrap():
    """
    This function has to be called before any other actions are attempted on
    packages. It ensures that the required directory structure is present.
    """

    ktr = Kentauros()

    # TODO: error handling

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

