from .result import KtrResult


class KtrValidator:
    def __init__(self, section: str, keys: list, binaries: list):
        self.section = section
        self.keys = keys
        self.binaries = binaries

    def validate(self) -> KtrResult:
        ret = KtrResult(name=self.section)
        success = True

        # TODO
        # copy from other modules, they all share the same code

        return ret.submit(success)
