from kentauros.config import KtrConfig
from kentauros.context import KtrContext
from .meta_package import KtrPackage


class KtrTestPackage(KtrPackage):
    def __init__(self, conf_name: str, context: KtrContext, conf: KtrConfig):
        super().__init__(context, conf_name)

        self.conf = conf
        self.name = self.conf.get("package", "name")
