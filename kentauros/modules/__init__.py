from .builder import get_builder
from .constructor import get_constructor
from .exporter import get_exporter
from .module import KtrModule
from .package import PackageModule
from .sources import get_source
from .uploader import get_uploader
from ..context import KtrContext
from ..package import KtrPackage


def _get_pkg_module(mtype: str, mimpl: str, pkg: KtrPackage, context: KtrContext) -> KtrModule:
    pkg_module_dict = dict()

    pkg_module_dict["source"] = get_source
    pkg_module_dict["constructor"] = get_constructor
    pkg_module_dict["builder"] = get_builder
    pkg_module_dict["uploader"] = get_uploader
    pkg_module_dict["exporter"] = get_exporter

    return pkg_module_dict[mtype](mimpl, pkg, context)


def get_module(mtype: str, mimpl: str, pkg: KtrPackage, context: KtrContext) -> KtrModule:
    if mtype == "package":
        return PackageModule(pkg, context)

    pkg_module = _get_pkg_module(mtype, mimpl, pkg, context)

    return pkg_module


__all__ = ["get_module"]
