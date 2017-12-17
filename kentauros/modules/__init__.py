"""
This subpackage contains all plug-able kentauros modules.
"""

import configparser as cp

from ..context import KtrContext
from ..definitions import PkgModuleType, SourceType, ConstructorType, BuilderType, UploaderType
from ..package import KtrPackage
from ..result import KtrResult

from .builder import get_builder
from .constructor import get_constructor
from .sources import get_source
from .uploader import get_uploader

from .module import KtrModule


def _get_pkg_module(mtype: PkgModuleType, stype, package: KtrPackage,
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

    return pkg_module_dict[mtype](stype, package, context)


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


def get_module(mtype: PkgModuleType, mimpl: str, package: KtrPackage,
               context: KtrContext) -> KtrModule:
    """
    This function constructs a `KtrModule` from a `PkgModuleType` enum member, an implementer
    string, and a package.
    """

    if mtype == PkgModuleType.PACKAGE:
        return PackageModule(package, context)

    pkg_module_type = _get_pkg_module_type(mtype)[mimpl]
    pkg_module = _get_pkg_module(mtype, pkg_module_type, package, context)

    return pkg_module


class PackageModule(KtrModule):
    NAME = "Package"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.actions["chain"] = self.execute
        self.actions["import"] = self.imports
        self.actions["status"] = self.status_string

        self.modules = list()

        try:
            modules = self.package.conf.get("package", "modules")
        except cp.ParsingError:
            modules = ""
        except cp.NoSectionError:
            modules = ""
        except cp.NoOptionError:
            modules = ""

        module_types = (PkgModuleType[i.upper()] for i in modules.split(","))

        if module_types == "":
            module_types = []

        for module_type in module_types:
            module_impl = self.package.conf.get("modules", str(module_type.name).lower())
            mod = get_module(module_type, module_impl.upper(), self.package, self.context)
            self.modules.append(mod)

    def name(self):
        return "{} {}".format(self.NAME, self.package.name)

    def __str__(self) -> str:
        return "{} '{}'".format(self.NAME, self.package.name)

    def execute(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for mod in self.modules:
            assert isinstance(mod, KtrModule)
            res = mod.execute()
            ret.collect(res)
            success = success and res.success

            if self.context.get_argument("force"):
                continue
            if not res.success:
                break

        return ret.submit(success)

    def clean(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for mod in self.modules:
            assert isinstance(mod, KtrModule)
            res = mod.clean()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

    def imports(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for mod in self.modules:
            assert isinstance(mod, KtrModule)
            res = mod.imports()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

    def status(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for mod in self.modules:
            assert isinstance(mod, KtrModule)
            res = mod.status()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

    def status_string(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        string = str()
        success = True

        res = self.package.status_string()
        ret.collect(res)

        if ret.success:
            string += ret.value

        for mod in self.modules:
            assert isinstance(mod, KtrModule)
            res = mod.status_string()
            ret.collect(res)

            if ret.success:
                string += ret.value

            success = success and res.success

        return ret.submit(success)

    def verify(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        res = self.package.verify()
        ret.collect(res)

        success = success and res.success

        for mod in self.modules:
            assert isinstance(mod, KtrModule)
            res = mod.verify()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)
