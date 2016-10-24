from kentauros.modules.pkgformatter.abstract import PkgFormatter


class RpmPkgFormatter(PkgFormatter):
    def __init__(self, package):
        super().__init__(package)

    def __str__(self) -> str:
        return ""

    def verify(self) -> bool:
        pass

    def imports(self) -> dict:
        pass

    def status(self) -> dict:
        pass

    def status_string(self) -> str:
        return ""

    def execute(self) -> bool:
        pass

    def clean(self) -> bool:
        pass
