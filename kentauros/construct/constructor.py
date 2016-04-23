"""
This module contains the template / dummy :py:class:`Constructor` class, which
is then inherited by actual constructors.
"""


class Constructor:
    """
    This class serves as a quasi-abstract base class for source package
    constructors. They are expected to override this class's methods as
    necessary.

    Arguments:
        Package package: package for which this constructor is for

    Attributes:
        Package pkg: stores parent package instance reference
    """

    def __init__(self, package):
        self.pkg = package

    def init(self):
        """
        This method creates the directory structure needed by other methods of
        this class.
        """
        pass

    def prepare(self, relreset: bool=False):
        """
        This method prepares all files necessary for the actual assembly of the
        source package.
        """
        pass

    def build(self):
        """
        This method assembles the source package from files prepared previously.
        """
        pass

    def export(self):
        """
        This method exports (moves) the assembled source packages to the
        specified package directory.
        """
        pass

    def clean(self):
        """
        This method cleans up all temporary files and directories.
        """
        pass

