from .context import KtrContext
from .modules.module import KtrModule
from .package import KtrPackage
from .result import KtrResult


class KtrTask:
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


class KtrTaskList:
    def __init__(self):
        self.tasks = list()

    def add(self, task: KtrTask):
        self.tasks.append(task)

    def execute(self) -> KtrResult:
        ret = KtrResult()
        success = True

        for task in self.tasks:
            assert isinstance(task, KtrTask)

            res = task.execute()
            ret.collect(res)
            success = success and res.success

        return ret.submit(success)
