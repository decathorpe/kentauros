from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from kentauros.result import KtrResult
from .module import KtrModule


class PackageModule(KtrModule):
    NAME = "Package"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.actions["chain"] = self.execute

    def name(self):
        return "{} {}".format(self.NAME, self.package.name)

    def __str__(self) -> str:
        return "{} '{}'".format(self.NAME, self.package.name)

    def execute(self) -> KtrResult:
        return KtrResult(True)

    def clean(self) -> KtrResult:
        return KtrResult(True)

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.package.status_string()
        ret.collect(res)

        ret.value = res.value
        return ret.submit(res.success)

    def verify(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.package.verify()
        ret.collect(res)

        return ret.submit(res.success)
