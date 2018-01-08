import abc
import enum
import os

from ..config import KtrConfig
from ..context import KtrContext
from ..result import KtrResult

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

    @abc.abstractmethod
    def verify(self) -> KtrResult:
        pass
