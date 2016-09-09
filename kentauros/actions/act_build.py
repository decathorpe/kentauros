"""
This submodule contains the :py:class:`BuildAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros
from kentauros.package import Package

from kentauros.actions.act_abstract import Action
from kentauros.actions.act_common import LOGPREFIX1


class BuildAction(Action):
    """
    This :py:class:`Action` subclass contains information for executing a local build of the package
    specified at initialisation.

    Arguments:
        Package kpkg:       package this local build will done for
        bool force:         currently without effect (common flag of actions)

    Attributes:
        ActionType atype:   here: stores ``ActionType.BUILD``
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.BUILD

    def execute(self) -> bool:
        """
        This method runs the local build corresponding to the package specified at initialisation,
        with the configuration from package configuration file. This method executes the
        :py:meth:`Builder.build()` method of the Builder instance in the specified package.

        Returns:
            bool:   ``True`` if all builds were successful, ``False`` otherwise
        """

        success = self.kpkg.builder.build()

        if not success:
            Kentauros(LOGPREFIX1).log("Binary package building unsuccessful, aborting action.", 2)

        return success