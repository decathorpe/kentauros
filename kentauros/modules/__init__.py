"""
This subpackage contains all plug-able kentauros modules.
"""


from kentauros.definitions import PkgModuleType
from kentauros.definitions import SourceType, ConstructorType, BuilderType, UploaderType

from kentauros.modules.sources import SOURCE_TYPE_DICT
from kentauros.modules.constructor import CONSTRUCTOR_TYPE_DICT
from kentauros.modules.builder import BUILDER_TYPE_DICT
from kentauros.modules.uploader import UPLOADER_TYPE_DICT


PKG_MODULE_DICT = dict()
PKG_MODULE_DICT[PkgModuleType.SOURCE] = SOURCE_TYPE_DICT
PKG_MODULE_DICT[PkgModuleType.CONSTRUCTOR] = CONSTRUCTOR_TYPE_DICT
PKG_MODULE_DICT[PkgModuleType.BUILDER] = BUILDER_TYPE_DICT
PKG_MODULE_DICT[PkgModuleType.UPLOADER] = UPLOADER_TYPE_DICT

PKG_MODULE_TYPE_DICT = dict()
PKG_MODULE_TYPE_DICT[PkgModuleType.SOURCE] = SourceType
PKG_MODULE_TYPE_DICT[PkgModuleType.CONSTRUCTOR] = ConstructorType
PKG_MODULE_TYPE_DICT[PkgModuleType.BUILDER] = BuilderType
PKG_MODULE_TYPE_DICT[PkgModuleType.UPLOADER] = UploaderType
