import configparser as cp

from .meta import KtrMetaTask
from .task import KtrTask
from ..context import KtrContext
from ..modules import get_module
from ..modules.module import KtrModule
from ..modules.package import PackageModule
from ..package import KtrPackage
from ..result import KtrResult


class KtrPackageTask(KtrMetaTask):
    def __init__(self, package: KtrPackage, action: str, context: KtrContext):
        self.context = context
        self.package = package

        self.modules = list()

        self.action = action

        try:
            modules = self.package.conf.get("package", "modules")
        except cp.ParsingError:
            modules = ""
        except cp.NoSectionError:
            modules = ""
        except cp.NoOptionError:
            modules = ""

        if modules == "":
            modules = []

        module_types = modules.split(",")

        self.modules.append(PackageModule(self.package, self.context))

        for module_type in module_types:
            module_impl = self.package.conf.get("modules", module_type)
            mod = get_module(module_type, module_impl, self.package, self.context)
            self.modules.append(mod)

    def execute(self) -> KtrResult:
        actions = {"chain": self._execute,
                   "clean": self._clean,
                   "import": self._imports,
                   "status": self._status_string,
                   "verify": self._verify}

        try:
            action = actions[self.action]
        except KeyError:
            ret = KtrResult()
            ret.messages.err("This action ({}) is not supported for packages.".format(self.action))
            return ret.submit(False)

        ret = KtrResult()
        ret.messages.log("Processing package: {}".format(self.package.conf_name))

        res = action()
        ret.collect(res)

        ret.messages.log("")

        return ret

    def _collect_action(self) -> KtrResult:
        # "simple" collecting action
        tasks = list()

        for module in self.modules:
            tasks.append(KtrTask(self.package, module, self.action, self.context))

        ret = KtrResult(True)

        for task in tasks:
            assert isinstance(task, KtrMetaTask)

            res = task.execute()
            ret.collect(res)

        return ret

    def _clean(self) -> KtrResult:
        return self._collect_action()

    def _imports(self) -> KtrResult:
        return self._collect_action()

    def _status(self) -> KtrResult:
        return self._collect_action()

    def _verify(self) -> KtrResult:
        return self._collect_action()

    def _execute(self) -> KtrResult:
        tasks = list()

        for module in self.modules:
            tasks.append(KtrTask(self.package, module, self.action, self.context))

        ret = KtrResult(True)

        for task in tasks:
            assert isinstance(task, KtrMetaTask)

            res = task.execute()
            ret.collect(res)

            if self.context.get_force():
                continue
            if not res.success:
                break

        return ret

    def _status_string(self) -> KtrResult:
        tasks = list()

        for module in self.modules:
            tasks.append(KtrTask(self.package, module, self.action, self.context))

        ret = KtrResult(True)
        string = str()

        res = self.package.status_string()
        ret.collect(res)

        if res.success:
            string += res.value

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.status_string()
            ret.collect(res)

        return ret
