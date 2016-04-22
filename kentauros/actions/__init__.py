"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its
subclasses, which are used to hold information about the action specified at
command line and are used to execute their respective actions. Additionally,
this file contains a dictionary which maps :py:class:``ActionType`` enums to
their respective class constructors.
"""


from kentauros.definitions import ActionType

from kentauros.actions.common import Action

from kentauros.actions.ktr import BuildAction, ChainAction, CleanAction
from kentauros.actions.ktr import ConstructAction, ExportAction, GetAction
from kentauros.actions.ktr import PrepareAction, RefreshAction, StatusAction
from kentauros.actions.ktr import UpdateAction, UploadAction, VerifyAction

from kentauros.actions.ktr_config import ConfigAction
from kentauros.actions.ktr_create import CreateAction


ACTION_DICT = dict()
"""This dictionary maps :py:class:`ActionType` enum members to their respective
action subclass constructors.
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

