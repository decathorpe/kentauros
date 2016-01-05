"""
kentauros.mock
"""

import glob
import os
import subprocess

from kentauros.base import goto_basedir, goto_pkgdir, err


def mock_build(pkgname, chroot=None):
    """
    kentauros.mock.mock_build()
    builds the srpm packages in package base directory in a mock chroot.
    returns True if all builds succeed, returns False if any build fails.
    """

    os.chdir("/etc/mock/")
    mock_chroots = glob.glob("*.cfg")
    cfgname = chroot + ".cfg"
    if cfgname not in mock_chroots:
        err("Specified chroot not available in mock. Aborting builds.")
        return False
    goto_basedir()

    goto_pkgdir(pkgname)
    src_rpms = glob.glob("*.src.rpm")

    builds_succ = list()
    builds_fail = list()

    if chroot:
        for src_rpm in src_rpms:
            ret = subprocess.call(["mock", "-r", chroot, src_rpm])
            if ret:
                builds_fail.append(src_rpm)
                err("Build failure:")
                err(chroot + "\t" + src_rpm)
            else:
                builds_succ.append(src_rpm)

    else:
        for src_rpm in src_rpms:
            ret = subprocess.call(["mock", src_rpm])
            if ret:
                builds_fail.append(src_rpm)
                err("Build failure:")
                err(chroot + "\t" + src_rpm)
            else:
                builds_succ.append(src_rpm)

    goto_basedir()

    if not builds_succ:
        print("The following builds succeeded:")
        for build_succ in builds_succ:
            print(build_succ)

    if not builds_fail:
        err("The following builds failed:")
        for build_fail in builds_fail:
            err(build_fail)
        return False
    else:
        return True

