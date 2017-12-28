import abc

from ..context import KtrContext
from ..package import KtrPackage
from ..result import KtrResult


class KtrModule(metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        assert isinstance(package, KtrPackage)
        assert isinstance(context, KtrContext)

        self.package = package
        self.context = context

        self.actions = {"clean": self.clean,
                        "import": self.imports,
                        "status": self.status_string,
                        "verify": self.verify}

    def act(self, action: str) -> KtrResult:
        return self.actions[action]()

    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def __str__(self) -> str:
        pass

    @abc.abstractmethod
    def execute(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def clean(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def status_string(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def imports(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def verify(self) -> KtrResult:
        pass
