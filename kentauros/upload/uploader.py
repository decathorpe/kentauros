"""
This module contains the template / dummy :py:class:`Uploader` class, which
is then inherited by actual uploaders.
"""


class Uploader:
    """
    This class serves as a quasi-abstract base class for source package
    uploaders. They are expected to override this class's methods as
    necessary.

    Arguments:
        Package package: package for which this constructor is for

    Attributes:
        Package pkg: stores parent package instance reference
    """

    def __init__(self, package):
        self.pkg = package

    def upload(self):
        """
        # TODO: napoleon method docstring
        kentauros.upload.Uploader.upload():
        method that uploads the package
        """
        pass

