from kentauros.config import KtrTestConfig
from kentauros.context import KtrTestContext
from kentauros.result import KtrResult
from .meta_package import KtrPackage


class KtrTestPackage(KtrPackage):
    def __init__(self, conf_name: str, conf: KtrTestConfig):
        super().__init__(KtrTestContext(), conf_name)

        self.conf = conf
        self.name = self.conf.get("package", "name")

    def verify(self) -> KtrResult:
        return KtrResult(True)
