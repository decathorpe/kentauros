from kentauros.config import KtrRealConfig
from kentauros.context import KtrContext
from .meta_package import KtrPackage


class KtrRealPackage(KtrPackage):
    def __init__(self, context: KtrContext, conf_name: str):
        super().__init__(context, conf_name)

        self.conf = KtrRealConfig(self.conf_path)
        self.name = self.conf.get("package", "name")
