"""
This submodule contains the :py:class:`VerifyAction` class.
"""


from ..definitions import ActionType
from ..instance import Kentauros
from ..logcollector import LogCollector
from ..result import KtrResult
from ..modules.module import PkgModule

from .abstract import Action


class VerifyAction(Action):
    """
    This `Action` subclass contains information for making sure the package's configuration file is
    valid and everything needed for actions is in place.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores `ActionType.VERIFY`
    """

    NAME = "Verify Action"

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.VERIFY

    def name(self) -> str:
        return self.NAME

    def execute(self) -> KtrResult:
        """
        This method executes a verification of the package configuration and checks if every file
        necessary for actions is present (and valid). The real checks are done during package
        initialisation.
        """

        ktr = Kentauros()
        logger = LogCollector(self.name())

        verify_success = True
        for module in self.kpkg.modules.values():
            assert isinstance(module, PkgModule)

            res: KtrResult = module.verify()
            logger.merge(res.messages)

            if res.success and ktr.cli.get_action() == ActionType.VERIFY:
                logger.log("Verification succeeded for module: " + str(module))

            if not res.success:
                logger.log("Verification failed for module: " + str(module))
                verify_success = False

        return KtrResult(verify_success, logger)
