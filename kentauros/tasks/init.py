from .meta import KtrMetaTask
from ..bootstrap import ktr_bootstrap
from ..context import KtrContext
from ..result import KtrResult


class KtrInitTask(KtrMetaTask):
    def __init__(self, context: KtrContext):
        self.context = context

    def execute(self) -> KtrResult:
        return ktr_bootstrap(self.context)
