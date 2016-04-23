"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its
subclasses, which are used to hold information about the action specified at
command line and are used to execute their respective actions. Additionally,
this file contains a dictionary which maps :py:class:`ActionType` enums to
their respective class constructors.
"""


from kentauros.definitions import ActionType

from kentauros.actions.action import Action

from kentauros.actions.std_actions import BuildAction
from kentauros.actions.std_actions import ChainAction
from kentauros.actions.std_actions import CleanAction
from kentauros.actions.std_actions import ConstructAction
from kentauros.actions.std_actions import ExportAction
from kentauros.actions.std_actions import GetAction
from kentauros.actions.std_actions import PrepareAction
from kentauros.actions.std_actions import RefreshAction
from kentauros.actions.std_actions import StatusAction
from kentauros.actions.std_actions import UpdateAction
from kentauros.actions.std_actions import UploadAction
from kentauros.actions.std_actions import VerifyAction

from kentauros.actions.config_action import ConfigAction
from kentauros.actions.create_action import CreateAction


ACTION_DICT = dict()
"""This dictionary maps :py:class:`ActionType` enum members to their respective
:py:class:`Action` subclass constructors.
"""

ACTION_DICT[ActionType.NONE] = Action
ACTION_DICT[ActionType.BUILD] = BuildAction
ACTION_DICT[ActionType.CHAIN] = ChainAction
ACTION_DICT[ActionType.CLEAN] = CleanAction
ACTION_DICT[ActionType.CONFIG] = ConfigAction
ACTION_DICT[ActionType.CONSTRUCT] = ConstructAction
ACTION_DICT[ActionType.CREATE] = CreateAction
ACTION_DICT[ActionType.EXPORT] = ExportAction
ACTION_DICT[ActionType.GET] = GetAction
ACTION_DICT[ActionType.PREPARE] = PrepareAction
ACTION_DICT[ActionType.REFRESH] = RefreshAction
ACTION_DICT[ActionType.STATUS] = StatusAction
ACTION_DICT[ActionType.UPDATE] = UpdateAction
ACTION_DICT[ActionType.UPLOAD] = UploadAction
ACTION_DICT[ActionType.VERIFY] = VerifyAction

