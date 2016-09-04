"""
This submodule contains the dummy :py:class:`DummyConstructor` class, which
executes nothing and acts as a placeholder.
"""


from kentauros.instance import Kentauros

from kentauros.construct.con_abstract import Constructor


LOGPREFIX1 = "ktr/construct/dummy: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class DummyConstructor(Constructor):
    """
    This :py:class:`Constructor` subclass is a dummy placeholder.

    Arguments:
        Package package: package for which this constructor is for

    Attributes:
        Package pkg: stores parent package instance reference
    """

    def __init__(self, package):
        super().__init__(package)

    def init(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Constructor for package " +
                        self.pkg + " initialised. Nothing happens.", 2)

    def prepare(self, relreset: bool=False, force: bool=False) -> bool:
        Kentauros().log(LOGPREFIX1 + "Dummy Constructor for package " +
                        self.pkg + " prepared. Nothing happens.", 2)

    def build(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Constructor for package " +
                        self.pkg + " executed. Nothing happens.", 2)

    def export(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Constructor for package " +
                        self.pkg + " exported. Nothing happens.", 2)

    def clean(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Constructor for package " +
                        self.pkg + " cleaned up. Nothing happens.", 2)
