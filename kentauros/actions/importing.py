"""
This submodule contains the :py:class:`ImportAction` class.
"""


from ..definitions import ActionType
from .abstract import Action


class ImportAction(Action):
    """
    This `Action` subclass contains methods for importing packages which are not yet configured for
    use with kentauros.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.IMPORT`
    """

    NAME = "Import Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.IMPORT

    def name(self) -> str:
        return self.NAME

    def execute(self) -> bool:
        """
        This method prints a pretty summary of a package's configuration values to the console.
        Currently, this does nothing whatsoever.
        """

        self.import_status()

        return True
