"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its subclasses, which are
used to hold information about the action specified at command line and are used to execute their
respective actions. Additionally, this file contains a dictionary which maps :py:class:`ActionType`
enums to their respective class constructors.
"""


from kentauros.definitions import ActionType

from kentauros.actions.act_build import BuildAction
from kentauros.actions.act_chain import ChainAction
from kentauros.actions.act_clean import CleanAction
from kentauros.actions.act_construct import ConstructAction
from kentauros.actions.act_export import ExportAction
from kentauros.actions.act_get import GetAction
from kentauros.actions.act_import import ImportAction
from kentauros.actions.act_prepare import PrepareAction
from kentauros.actions.act_refresh import RefreshAction
from kentauros.actions.act_status import StatusAction
from kentauros.actions.act_update import UpdateAction
from kentauros.actions.act_upload import UploadAction
from kentauros.actions.act_verify import VerifyAction


ACTION_DICT = dict()
"""This dictionary maps :py:class:`ActionType` enum members to their respective :py:class:`Action`
subclass constructors.
"""

ACTION_DICT[ActionType.BUILD] = BuildAction
ACTION_DICT[ActionType.CHAIN] = ChainAction
ACTION_DICT[ActionType.CLEAN] = CleanAction
ACTION_DICT[ActionType.CONSTRUCT] = ConstructAction
ACTION_DICT[ActionType.EXPORT] = ExportAction
ACTION_DICT[ActionType.GET] = GetAction
ACTION_DICT[ActionType.IMPORT] = ImportAction
ACTION_DICT[ActionType.PREPARE] = PrepareAction
ACTION_DICT[ActionType.REFRESH] = RefreshAction
ACTION_DICT[ActionType.STATUS] = StatusAction
ACTION_DICT[ActionType.UPDATE] = UpdateAction
ACTION_DICT[ActionType.UPLOAD] = UploadAction
ACTION_DICT[ActionType.VERIFY] = VerifyAction
