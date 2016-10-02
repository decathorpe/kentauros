"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its subclasses, which are
used to hold information about the action specified at command line and are used to execute their
respective actions. Additionally, this file contains a dictionary which maps :py:class:`ActionType`
enums to their respective class constructors.
"""


from kentauros.definitions import ActionType

from kentauros.actions.build import BuildAction
from kentauros.actions.chain import ChainAction
from kentauros.actions.clean import CleanAction
from kentauros.actions.construct import ConstructAction
from kentauros.actions.export import ExportAction
from kentauros.actions.get import GetAction
from kentauros.actions.importing import ImportAction
from kentauros.actions.prepare import PrepareAction
from kentauros.actions.refresh import RefreshAction
from kentauros.actions.status import StatusAction
from kentauros.actions.update import UpdateAction
from kentauros.actions.upload import UploadAction
from kentauros.actions.verify import VerifyAction


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
