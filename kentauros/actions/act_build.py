"""
This submodule contains the :py:class:`BuildAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.instance import Kentauros

from kentauros.actions.act_abstract import Action
from kentauros.actions.act_common import LOGPREFIX


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

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.BUILD

    def execute(self) -> bool:
        """
        This method runs the local build corresponding to the package specified at initialisation,
        with the configuration from package configuration file. This method executes the
        :py:meth:`Builder.build()` method of the Builder instance in the specified package.

        Returns:
            bool:   ``True`` if all builds were successful, ``False`` otherwise
        """

        ktr = Kentauros(LOGPREFIX)

        success = self.kpkg.builder.build()

        if not success:
            ktr.log("Binary package building unsuccessful, aborting action.")
            return False

        success = self.kpkg.builder.export()

        if not success:
            ktr.log("Binary package exporting unsuccessful, aborting action.")
            return False

        return success
