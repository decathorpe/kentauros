"""
This module contains all definitions of types and global variables that are used by nearly every
other module / subpackage.

It includes these globally used variables:

* ``KTR_SYSTEM_DATADIR``:   directory where kentauros data is installed to resides when installed
* ``KTR_VERSION``:          this version string is used when installing and packaging kentauros
"""


KTR_SYSTEM_DATADIR = "/usr/share/kentauros/"
"""This string represents the absolute path which kentauros data files are
copied to at installation and where they are expected to be when running ktr.
"""

KTR_VERSION = "1.0.7"
"""This string represents the version string used by ``setup.py`` at install
time and ``make-srpm.sh`` when building an srpm package. The version in
``kentauros.spec`` has to be set manually yet.
"""
