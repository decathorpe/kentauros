from ..result import KtrResult
from .meta import KtrMetaTask


class KtrNoTask(KtrMetaTask):
    def execute(self) -> KtrResult:
        ret = KtrResult(False)
        ret.messages.log("No action specified. Exiting.")
        return ret
