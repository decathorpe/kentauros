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
        # TODO: napoleon method docstring
        kentauros.construct.Constructor.init()
        method that creates directories needed for source package building
        """
        pass

    def prepare(self, relreset: bool=False):
        """
        # TODO: napoleon method docstring
        kentauros.construct.Constructor.prepare()
        method that copies files needed for source package building
        """
        pass

    def build(self):
        """
        # TODO: napoleon method docstring
        kentauros.construct.Constructor.build()
        method that builds source package
        """
        pass

    def export(self):
        """
        # TODO: napoleon method docstring
        kentauros.construct.Constructor.export()
        method that moves built source package
        """
        pass

    def clean(self):
        """
        # TODO: napoleon method docstring
        kentauros.construct.Constructor.clean()
        method that cleans up temporary files
        """
        pass

