import abc
import configparser as cp

from .context import KtrContext
from .definitions import PkgModuleType
from .modules import get_module
from .modules.module import KtrModule
from .modules.package import PackageModule
from .package import KtrPackage
from .result import KtrResult


class KtrMetaTask(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def execute(self) -> KtrResult:
        pass


class KtrTask(KtrMetaTask):
    def __init__(self, package: KtrPackage, module: KtrModule, action: str, context: KtrContext):

        self.context = context
        self.package = package

        self.module = module
        self.action = action

    def execute(self) -> KtrResult:
        ret = self.module.act(self.action)

        if ret.success:
            self.context.state.write(self.package.conf_name, ret.state)

        return ret


class KtrTaskList(KtrMetaTask):
    def __init__(self):
        self.tasks = list()

    def add(self, task: KtrMetaTask):
        self.tasks.append(task)

    def execute(self) -> KtrResult:
        ret = KtrResult()
        success = True

        for task in self.tasks:
            assert isinstance(task, KtrMetaTask)

            res = task.execute()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)


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

        module_types = (PkgModuleType[i.upper()] for i in modules.split(","))

        self.modules.append(PackageModule(self.package, self.context))
        for module_type in module_types:
            module_impl = self.package.conf.get("modules", str(module_type.name).lower())
            mod = get_module(module_type, module_impl.upper(), self.package, self.context)
            self.modules.append(mod)

    def execute(self) -> KtrResult:
        actions = {"chain": self._execute,
                   "clean": self._clean,
                   "import": self._imports,
                   "status": self._status_string,
                   "verify": self._verify}

        try:
            return actions[self.action]()
        except KeyError:
            ret = KtrResult()
            ret.messages.err("This action ({}) is not supported for packages.".format(self.action))
            return ret.submit(False)

    def _collect_action(self) -> KtrResult:
        # "simple" collecting action
        tasks = list()

        for module in self.modules:
            tasks.append(KtrTask(self.package, module, self.action, self.context))

        ret = KtrResult()
        success = True

        for task in tasks:
            assert isinstance(task, KtrMetaTask)

            res = task.execute()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)

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

        ret = KtrResult()
        success = True

        for task in tasks:
            assert isinstance(task, KtrMetaTask)

            res = task.execute()
            ret.collect(res)
            success = success and res.success

            if self.context.get_argument("force"):
                continue
            if not res.success:
                break

        return ret.submit(success)

    def _status_string(self) -> KtrResult:
        tasks = list()

        for module in self.modules:
            tasks.append(KtrTask(self.package, module, self.action, self.context))

        ret = KtrResult()
        string = str()
        success = True

        res = self.package.status_string()
        ret.collect(res)

        if res.success:
            string += res.value

        for module in self.modules:
            assert isinstance(module, KtrModule)
            res = module.status_string()
            ret.collect(res)

            if res.success:
                string += res.value

            success = success and res.success

        return ret.submit(success)
