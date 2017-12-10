"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its subclasses, which are
used to hold information about the action specified at command line and are used to execute their
respective actions. Additionally, this file contains a dictionary which maps :py:class:`ActionType`
enums to their respective class constructors.
"""


from ..definitions import ActionType

from .abstract import Action
from .build import BuildAction
from .chain import ChainAction
from .clean import CleanAction
from .construct import ConstructAction
from .importing import ImportAction
from .prepare import PrepareAction
from .status import StatusAction
from .upload import UploadAction
from .verify import VerifyAction


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
