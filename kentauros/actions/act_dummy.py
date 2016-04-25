"""
This submodule contains the dummy :py:class:`DummyAction` class, which executes
nothing and acts as a placeholder.
"""


from kentauros.definitions import ActionType
from kentauros.instance import log

from kentauros.package import Package
from kentauros.actions.act_abstract import Action
from kentauros.actions.act_common import LOGPREFIX1


class DummyAction(Action):
    """
    This :py:class:`Action` subclass is a dummy placeholder.

    Arguments:
        Package kpkg:       package nothing will be done for
        bool force:         currently without effect (common flag of actions)

    Attributes:
        Package kpkg:       stores reference to package given at initialisation
        bool force:         stores force value given at initialisation
        ActionType atype:   stores type of action as enum
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.DUMMY

    def execute(self):
        """
        This method prints that it was tried to execute a DummyAction, which
        should not happen.
        """

        log(LOGPREFIX1 + "Dummy Action executed. Nothing happens.", 2)

