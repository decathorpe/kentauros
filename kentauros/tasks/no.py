import logging

from kentauros.result import KtrResult
from .meta import KtrMetaTask


class KtrNoTask(KtrMetaTask):
    def __init__(self):
        self.logger = logging.getLogger("ktr/task/none")

    def execute(self) -> KtrResult:
        ret = KtrResult(False)
        self.logger.info("No action specified. Exiting.")
        return ret
