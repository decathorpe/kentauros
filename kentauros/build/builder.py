"""
This module contains the template / dummy :py:class:`Builder` class, which
is then inherited by actual builders.
"""


class Builder:
    """
    # TODO: napoleon class docstring
    kentauros.build.Builder:
    base class for source package builders
    """

    def __init__(self, package):
        self.package = package

    def build(self):
        """
        # TODO: napoleon method docstring
        kentauros.build.Builder.build():
        method that runs the package build
        """
        pass

    def export(self):
        """
        # TODO: napoleon method docstring
        kentauros.build.Builder.export():
        method that exports built packages
        """
        pass

