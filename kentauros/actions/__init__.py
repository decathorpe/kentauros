"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its subclasses, which are
used to hold information about the action specified at command line and are used to execute their
respective actions. Additionally, this file contains a dictionary which maps :py:class:`ActionType`
enums to their respective class constructors.
"""


from kentauros.definitions import ActionType

from kentauros.actions.abstract import Action
from kentauros.actions.build import BuildAction
from kentauros.actions.chain import ChainAction
from kentauros.actions.clean import CleanAction
from kentauros.actions.construct import ConstructAction
from kentauros.actions.importing import ImportAction
from kentauros.actions.prepare import PrepareAction
from kentauros.actions.status import StatusAction
from kentauros.actions.upload import UploadAction
from kentauros.actions.verify import VerifyAction


def get_action(action_type: ActionType, name: str) -> Action:
    """
    This function constructs an `Action` from an `ActionType` enum member and a package name.
    """

    action_dict = dict()

    action_dict[ActionType.PREPARE] = PrepareAction
    action_dict[ActionType.CONSTRUCT] = ConstructAction
    action_dict[ActionType.BUILD] = BuildAction
    action_dict[ActionType.UPLOAD] = UploadAction

    action_dict[ActionType.CHAIN] = ChainAction
    action_dict[ActionType.CLEAN] = CleanAction

    action_dict[ActionType.IMPORT] = ImportAction
    action_dict[ActionType.STATUS] = StatusAction
    action_dict[ActionType.VERIFY] = VerifyAction

    return action_dict[action_type](name)
