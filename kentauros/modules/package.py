from ..context import KtrContext
from ..definitions import PkgModuleType
from ..package import KtrPackage
from ..result import KtrResult

from .module import KtrModule
from . import get_module


class PackageModule(KtrModule):
    NAME = "Package"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.actions["chain"] = self.execute
        self.actions["import"] = self.imports
        self.actions["status"] = self.status_string

        self.modules = list()

        module_types = (PkgModuleType[i.upper()] for i
                        in self.package.conf.get("main", "modules").split(","))

        if module_types == "":
            module_types = []

        for module_type in module_types:
            module_impl = self.package.conf.get("modules", str(module_type.name).lower())
            module = get_module(module_type, module_impl.upper(), self.package, self.context)
            self.modules.append(module)

    def name(self):
        return "{} {}".format(self.NAME, self.package.name)

    def __str__(self) -> str:
        return "{} '{}'".format(self.NAME, self.package.name)

    def execute(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.execute()
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

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.clean()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

    def imports(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.imports()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

    def status(self) -> KtrResult:
        ret = KtrResult(name=self.name())
        success = True

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.status()
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

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.status_string()
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

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.verify()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)
