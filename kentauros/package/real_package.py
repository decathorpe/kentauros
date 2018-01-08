from .meta_package import KtrPackage
from ..config import KtrRealConfig
from ..context import KtrContext
from ..result import KtrResult
from ..validator import KtrValidator


class KtrRealPackage(KtrPackage):
    def __init__(self, context: KtrContext, conf_name: str):
        super().__init__(context, conf_name)

        self.conf = KtrRealConfig(self.conf_path)
        self.name = self.conf.get("package", "name")

    def verify(self) -> KtrResult:
        name = "Package {}".format(self.conf_name)
        ret = KtrResult(True, name=name)

        conf = self.conf.conf

        # check [package] section
        package_expected_keys = ["name", "version", "release", "modules"]

        package_validator = KtrValidator(conf, "package", package_expected_keys)
        res = package_validator.validate()
        ret.collect(res)

        # check validity of [package][release] option ("stable", "post", or "pre")
        if conf.has_section("package") and conf.has_option("package", "release"):
            release_types = ["stable", "post", "pre"]
            ret.success = ret.success and (conf.get("package", "release") in release_types)
        # check [modules] section, if present
        if conf.has_section("package") and conf.has_option("package", "modules"):
            modules: str = conf.get("package", "modules")

            if modules == "":
                modules_expected_keys = []
            else:
                modules_expected_keys = modules.split(",")

            modules_validator = KtrValidator(conf, "modules", modules_expected_keys)
            res = modules_validator.validate()
            ret.collect(res)

            # check if sections for all modules exist
            modules = modules_expected_keys

            for module in modules:
                if not conf.has_section(module):
                    ret.success = False

        return ret
