"""
# TODO: napoleon module docstring
"""


class Constructor:
    """
    # TODO: napoleon class docstring
    kentauros.construct.Constructor:
    base class for source package preparators
    """
    def __init__(self, package):
        self.package = package

    def init(self):
        """
        # TODO: napoleon method docstring
        kentauros.construct.Constructor.init()
        method that creates directories needed for source package building
        """
        pass

    def prepare(self, relreset=False):
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

