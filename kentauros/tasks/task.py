from .meta import KtrMetaTask
from ..context import KtrContext
from ..modules.module import KtrModule
from ..package import KtrPackage
from ..result import KtrResult


class KtrTask(KtrMetaTask):
    def __init__(self, package: KtrPackage, module: KtrModule, action: str, context: KtrContext):
        self.context = context
        self.package = package

        self.module = module
        self.action = action

    def execute(self) -> KtrResult:
        ret = KtrResult()
        ret.messages.log("Processing package: {}".format(self.package.conf_name))

        res = self.module.act(self.action)
        ret.collect(res)

        ret.messages.log("")

        if ret.success:
            self.context.state.write(self.package.conf_name, ret.state)

        return ret
