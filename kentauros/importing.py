"""
This module contains code for importing packages into the package database.
"""


from kentauros.instance import Kentauros
# from kentauros.logger import KtrLogger


def check_package(pkg_name: str):
    """
    This function checks if a package with the given configuration name already exists in the
    package database.

    Arguments:
        str pkg_name:   configuration name to check for

    Returns:
        bool:           *True* if the package already exists, *False* if not
    """

    assert isinstance(pkg_name, str)

    ktr = Kentauros()
    return pkg_name in ktr.get_package_names()


def import_package(pkg_name: str):
    """
    This function adds a package, which must not be in the database already, to the database of
    known packages.

    Arguments:
        str pkg_name:   configuration name to insert with
    """

    assert isinstance(pkg_name, str)
    # TODO: get fallback status values from all package modules
