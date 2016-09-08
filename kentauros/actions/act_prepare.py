"""
This submodule contains the :py:class:`PrepareAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.package import Package

from kentauros.actions.act_abstract import Action


class PrepareAction(Action):
    """
    This `Action` subclass contains information for preparing the package's sources. Sources will be
    downloaded or copied to destination, updated if already there, and exported to a tarball, if
    necessary.

    Arguments:
        Package kpkg:       package for which source preparation is done
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.PREPARE`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.PREPARE

    def execute(self) -> bool:
        """
        This method executes the :py:meth:`Source.prepare()` method to execute source preparation.
        This includes downloading or copying to destination, updating if necessary, and exporting to
        tarball if necessary.

        Returns:
            bool:           *True* when successful, *False* if sub-action fails
        """

        return self.kpkg.source.prepare()
