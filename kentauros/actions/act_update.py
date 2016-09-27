"""
This submodule contains the :py:class:`UpdateAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.package import Package

from kentauros.actions.act_abstract import Action


class UpdateAction(Action):
    """
    This `Action` subclass contains information for updating the package's source as specified in
    the package configuration. This only has effect for VCS sources, which will pull upstream
    changes as specified.

    Arguments:
        Package kpkg:       Package instance source update will be run for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.UPDATE`
    """

    def __init__(self, kpkg: Package):
        super().__init__(kpkg)
        self.atype = ActionType.UPDATE

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.update()` method to execute the source updating,
        if possible - this only has effect for sources with an upstream VCS specified as origin.

        Returns:
            bool:   *True* when update was available, *False* if not or failure
        """

        update = self.kpkg.source.update()
        return update
