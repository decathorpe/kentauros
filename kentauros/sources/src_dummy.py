"""
This submodule contains the dummy :py:class:`DummySource` class, which executes
nothing and acts as a placeholder.
"""


from kentauros.definitions import SourceType
from kentauros.instance import Kentauros

from kentauros.sources.src_abstract import Source


LOGPREFIX1 = "ktr/sources/dummy: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class DummySource(Source):
    """
    This :py:class:`Source` subclass is a dummy placeholder.

    Arguments:
        Package package:    package to which this source belongs

    Attributes:
        Package package:    stores the package argument given at initialisation
    """

    def __init__(self, package):
        super().__init__(package)
        self.stype = SourceType.NONE

    def clean(self) -> bool:
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " cleaned. Nothing happens.", 2)
        return True

    def export(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " exported. Nothing happens.", 2)
        return True

    def status(self) -> dict:
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " queried. Nothing happens.", 2)
        return dict()

    def get(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " got. Nothing happens.", 2)
        return True

    def update(self):
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " updated. Nothing happens.", 2)
        return True

    def formatver(self) -> str:
        return self.spkg.conf.get("source", "version")

    def prepare(self) -> bool:
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " prepared. Nothing happens.", 2)
        return True

    def refresh(self) -> bool:
        Kentauros().log(LOGPREFIX1 + "Dummy Source for package " +
                        self.spkg + " refreshed. Nothing happens.", 2)
        return True
