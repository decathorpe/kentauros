"""
This module contains code for importing packages into the package database.
"""


from kentauros.instance import Kentauros
# from kentauros.logger import KtrLogger


def check_package(pkg_name: str):
    assert isinstance(pkg_name, str)

    ktr = Kentauros()
    return pkg_name in ktr.get_package_names()


def import_package(pkg_name: str):
    assert isinstance(pkg_name, str)

    ktr = Kentauros()
    package = ktr.get_package(pkg_name)
    ktr.state_write(pkg_name, package.status())
    ktr.state_write(pkg_name, package.source.status())
