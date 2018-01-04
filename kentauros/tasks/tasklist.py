from .meta import KtrMetaTask
from .task import KtrTask
from ..result import KtrResult


class KtrTaskList(KtrMetaTask):
    def __init__(self):
        self.tasks = list()

    def add(self, task: KtrMetaTask):
        self.tasks.append(task)

    def execute(self) -> KtrResult:
        ret = KtrResult()

        for task in self.tasks:
            assert isinstance(task, KtrMetaTask)

            res = task.execute()
            ret.collect(res)

        return ret
