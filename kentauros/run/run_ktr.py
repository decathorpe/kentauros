"""
This module contains the :py:func:`run` function that is called as entry point from the ``ktr``
script.
"""


import glob
import os

from kentauros.instance import Kentauros

from kentauros.actions import ACTION_DICT
from kentauros.bootstrap import ktr_bootstrap
from kentauros.package import Package


LOGPREFIX1 = "ktr: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""

LOGPREFIX2 = "     - "
"""This string specifies the prefix for lists printed through log and error
functions, printed to stdout or stderr from inside this subpackage.
"""


def run():
    """
    This function is corresponding to (one of) the "main" function of the
    `kentauros` package and is the entry point used by the ``ktr`` script from
    git and the script installed by setuptools at installation.
    """

    ktr = Kentauros(LOGPREFIX1)

    print()

    ktr.log("DEBUG set: " + str(ktr.debug), 0)
    ktr.log("VERBOSITY: " + str(ktr.verby) + "/2", 1)

    ktr.dbg("BASEDIR: " + ktr.conf.basedir)
    ktr.dbg("CONFDIR: " + ktr.conf.get_confdir())
    ktr.dbg("DATADIR: " + ktr.conf.get_datadir())
    ktr.dbg("PACKDIR: " + ktr.conf.get_packdir())
    ktr.dbg("SPECDIR: " + ktr.conf.get_specdir())

    # if no action is specified: exit
    if ktr.cli.get_action() is None:
        ktr.log("No action specified. Exiting.", 2)
        ktr.log("Use 'ktr --help' for more information.", 2)
        print()
        return

    if not ktr_bootstrap():
        raise SystemExit

    pkgs = list()

    # if only specified packages are to be processed:
    # process packages only
    if not ktr.cli.get_packages_all():
        for name in ktr.cli.get_packages():
            pkgs.append(name)

    # if all package are to be processed:
    # get package configs present in CONFDIR
    else:
        pkg_conf_paths = glob.glob(os.path.join(
            ktr.conf.get_confdir(), "*.conf"))

        for pkg_conf_path in pkg_conf_paths:
            pkgs.append(os.path.basename(pkg_conf_path).replace(".conf", ""))

    # log list of found packages
    ktr.log("Packages:", 2)
    for package in pkgs:
        assert isinstance(package, str)
        ktr.log(package, pri=2, prefix=LOGPREFIX2)

    # run action for every specified package
    for name in pkgs:
        assert isinstance(name, str)

        action_type = ktr.cli.get_action()
        action = ACTION_DICT[action_type](Package(name), ktr.cli.get_force())
        success = action.execute()

        if success:
            ktr.log(name + ": Success!")
        else:
            ktr.log(name + ": Not successful.")

    print()
