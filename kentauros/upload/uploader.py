"""
This module contains the template / dummy :py:class:`Uploader` class, which
is then inherited by actual uploaders.
"""


class Uploader:
    """
    # TODO: napoleon class docstring
    kentauros.upload.Uploader:
    base class for source package uploaders
    """
    def __init__(self, package):
        self.package = package

    def upload(self):
        """
        # TODO: napoleon method docstring
        kentauros.upload.Uploader.upload():
        method that uploads the package
        """
        pass

