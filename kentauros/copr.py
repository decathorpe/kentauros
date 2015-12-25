"""
kentauros.copr
"""

import glob
import subprocess

from kentauros.base import goto_basedir, goto_pkgdir
from kentauros.conf import get_pkgcopr, get_coprrepo


def copr_build(pkgname, wait=False):
    """
    kentauros.copr.copr_build()
    uploads and builds all srpms in package base directory
    """
    pkgcopr = get_pkgcopr(pkgname)

    if not pkgcopr:
        return None

    coprrepo = get_coprrepo(pkgname)

    goto_pkgdir(pkgname)

    src_rpms = glob.glob("*.src.rpm")

    for src_rpm in src_rpms:
        if wait:
            subprocess.call(["copr-cli", "build", coprrepo, src_rpm])
        else:
            subprocess.call(["copr-cli", "build", "--nowait", coprrepo, src_rpm])
        subprocess.call(["rm", src_rpm])

    goto_basedir()

