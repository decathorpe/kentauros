"""
This submodule contains the dummy :py:class:`DummyBuilder` class, which executes
nothing and acts as a placeholder.
"""


from kentauros.instance import Kentauros

from kentauros.build.bld_abstract import Builder


LOGPREFIX1 = "ktr/build/dummy: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class DummyBuilder(Builder):
    """
    This :py:class:`Builder` subclass is a dummy placeholder.

    Arguments:
        Package package:    package to which this builder belongs

    Attributes:
        Package package:    stores the package argument given at initialisation
    """

    def __init__(self, package):
        super().__init__(package)

    def build(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Builder for package " +
                        self.bpkg + " executed. Nothing happens.", 2)

    def export(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Builder for package " +
                        self.bpkg + " exported. Nothing happens.", 2)

