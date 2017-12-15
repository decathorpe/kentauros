from .context import KtrContext
# from .logcollector import LogCollector
from .modules.module import PkgModule
from .package import Package
from .result import KtrResult


class KtrTask:
    def __init__(self, package: Package, module: PkgModule,
                 actions: list, context: KtrContext):

        self.package = package
        self.module = module
        self.actions = actions
        self.context = context

    def execute(self) -> KtrResult:
        pass
