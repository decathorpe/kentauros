import abc
import enum
import os

from kentauros.config import KtrConfig
from kentauros.context import KtrContext
from kentauros.result import KtrResult
from kentauros.validator import KtrValidator

PACKAGE_STATUS_TEMPLATE = """
Configuration:      {conf_name}
------------------------------------------------------------
  Package name:     {name}
  Package version:  {version}
  Release type:     {release_type}
""".lstrip("\n")


class ReleaseType(enum.Enum):
    STABLE = 0
    POST = 1
    PRE = 2


class KtrPackage(metaclass=abc.ABCMeta):
    def __init__(self, context: KtrContext, conf_name: str):
        assert isinstance(context, KtrContext)
        assert isinstance(conf_name, str)

        self.context = context
        self.conf_name = conf_name

        self.conf_path = os.path.join(self.context.get_confdir(), self.conf_name + ".conf")

        self.conf: KtrConfig = None
        self.name: str = None

    def verify(self) -> KtrResult:
        ret = KtrResult(True)

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
                if not conf.has_option("modules", module):
                    ret.success = False

        return ret

    def get_version(self) -> str:
        return self.conf.get("package", "version")

    def get_release_type(self) -> ReleaseType:
        return ReleaseType[self.conf.get("package", "release").upper()]

    def get_version_separator(self) -> str:
        release_type = self.get_release_type()

        separator_dict = dict()
        separator_dict[ReleaseType.STABLE] = ""
        separator_dict[ReleaseType.POST] = self.context.conf.get("main", "version_separator_post")
        separator_dict[ReleaseType.PRE] = self.context.conf.get("main", "version_separator_pre")

        return separator_dict[release_type]

    def replace_vars(self, input_str: str) -> str:
        output_str = input_str

        if "%{name}" in output_str:
            output_str = output_str.replace("%{name}", self.name)

        if "%{version}" in output_str:
            output_str = output_str.replace("%{version}", self.get_version())

        return output_str

    def status(self) -> KtrResult:
        state = dict(package_name=self.name,
                     package_version=self.get_version())

        return KtrResult(True, state=state)

    def status_string(self) -> KtrResult:
        string = PACKAGE_STATUS_TEMPLATE.format(conf_name=self.conf_name,
                                                name=self.name,
                                                version=self.get_version(),
                                                release_type=str(self.get_release_type()))

        return KtrResult(True, string)
