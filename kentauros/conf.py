"""
kentauros.conf
"""

from configparser import ConfigParser

from kentauros.base import dbg
from kentauros.base import goto_basedir, goto_pkgdir


#class PkgConf(ConfigParser):
#    """
#    kentauros.PkgConf
#    This class is an object that holds all available configuration information
#    about one package.
#    """


def get_confval(pkgname, section, key):
    """
    kentauros.conf.get_confval
    generic function that reads a value from a package config file
    """
    dbg("Getting value from config file: [" + section + "]: " + key)
    assert isinstance(section, str)
    assert isinstance(key, str)

    goto_pkgdir(pkgname)
    pkgconfig = ConfigParser()
    pkgconfig.read(pkgname + ".conf")
    value = pkgconfig[section][key]
    goto_basedir()

    dbg("Got value from config file: [" + section + "]: " + key + ": " + value)
    return value


def get_pkgvers(pkgname):
    """
    kentauros.conf.get_pkgvers
    function that reads the package version from the package config file
    """
    return get_confval(pkgname, "package", "version")

def get_pkgcopr(pkgname):
    """
    kentauros.conf.pkgcopr
    function that determines whether copr functionality should be enabled
    """
    return bool(get_confval(pkgname, "package", "copr"))

def get_srcname(pkgname):
    """
    kentauros.conf.get_srcname
    function that reads the source name from the package config file
    """
    return get_confval(pkgname, "source", "name")

def get_srctype(pkgname):
    """
    kentauros.conf.get_srctype
    function that reads the source type from the package config file
    """
    return get_confval(pkgname, "source", "type")

def get_srcorig(pkgname):
    """
    kentauros.conf.get_srcorig
    function that reads the source origin from the package config file
    """
    return get_confval(pkgname, "source", "origin")

def get_srckeep(pkgname):
    """
    kentauros.conf.get_srckeep
    function that determines whether the sources should be kept between runs
    """
    return bool(get_confval(pkgname, "source", "keep"))

def get_copruser(pkgname):
    """
    kentauros.conf.get_copruser
    function that reads the copr username from the package config file
    """
    return get_confval(pkgname, "copr", "user")

def get_coprrepo(pkgname):
    """
    kentauros.conf.get_coprrepo
    function that reads the copr repository name from the package config file
    """
    return get_confval(pkgname, "copr", "repo")

