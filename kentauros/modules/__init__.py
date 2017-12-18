"""
This subpackage contains all plug-able kentauros modules.
"""

from ..context import KtrContext
from ..definitions import PkgModuleType, SourceType, ConstructorType, BuilderType, UploaderType
from ..package import KtrPackage

from .builder import get_builder
from .constructor import get_constructor
from .sources import get_source
from .uploader import get_uploader

from .module import KtrModule
from .package import PackageModule


def _get_pkg_module(mtype: PkgModuleType, stype, pkg: KtrPackage,
                    context: KtrContext) -> KtrModule:
    """
    This function constructs a `KtrModule` from a `PkgModuleType` enum member, a `PkgModuleType`
    subtype, and a package.
    """

    pkg_module_dict = dict()

    pkg_module_dict[PkgModuleType.SOURCE] = get_source
    pkg_module_dict[PkgModuleType.CONSTRUCTOR] = get_constructor
    pkg_module_dict[PkgModuleType.BUILDER] = get_builder
    pkg_module_dict[PkgModuleType.UPLOADER] = get_uploader

    return pkg_module_dict[mtype](stype, pkg, context)


def _get_pkg_module_type(mtype: PkgModuleType):
    """
    This function constructs a `PkgModuleType` subtype from a `PkgModuleType` enum member.
    """

    pkg_module_type_dict = dict()

    pkg_module_type_dict[PkgModuleType.SOURCE] = SourceType
    pkg_module_type_dict[PkgModuleType.CONSTRUCTOR] = ConstructorType
    pkg_module_type_dict[PkgModuleType.BUILDER] = BuilderType
    pkg_module_type_dict[PkgModuleType.UPLOADER] = UploaderType

    return pkg_module_type_dict[mtype]


def get_module(mtype: PkgModuleType, mimpl: str, pkg: KtrPackage,
               context: KtrContext) -> KtrModule:
    """
    This function constructs a `KtrModule` from a `PkgModuleType` enum member, an implementer
    string, and a package.
    """

    if mtype == PkgModuleType.PACKAGE:
        return PackageModule(pkg, context)

    pkg_module_type = _get_pkg_module_type(mtype)[mimpl]
    pkg_module = _get_pkg_module(mtype, pkg_module_type, pkg, context)

    return pkg_module
