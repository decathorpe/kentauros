import logging

from kentauros.modules import get_module
from kentauros.package import KtrRealPackage
from kentauros.tasks import KtrMetaTask, KtrTask, KtrInitTask, KtrNoTask
from kentauros.tasks import KtrTaskList, KtrPackageTask, KtrPackageAddTask
from .cli_context import KtrCLIContext


class KtrCLIRunner:
    def __init__(self):
        self.context = KtrCLIContext()

        conf_names = self.context.get_packages()
        module_type = self.context.get_module()

        if module_type is None:
            self.task = KtrNoTask()

        elif module_type == "init":
            self.task = KtrInitTask(self.context)

        elif module_type == "package":
            action = self.context.get_module_action()

            self.task: KtrTaskList = KtrTaskList()

            if action == "add":
                for conf_name in conf_names:
                    task = KtrPackageAddTask(conf_name, self.context)
                    self.task.add(task)

            else:
                for conf_name in conf_names:
                    package = KtrRealPackage(self.context, conf_name)
                    task = KtrPackageTask(package, action, self.context)
                    self.task.add(task)
        else:
            action = self.context.get_module_action()
            self.task: KtrTaskList = KtrTaskList()

            for conf_name in conf_names:
                package = KtrRealPackage(self.context, conf_name)
                module_impl = package.conf.get("modules", module_type)
                module = get_module(module_type, module_impl, package, self.context)
                task = KtrTask(package, module, action, self.context)

                self.task.add(task)

    def _run_task(self) -> int:
        assert isinstance(self.task, KtrMetaTask)
        assert not isinstance(self.task, KtrTaskList)

        result = self.task.execute()

        if result.success:
            return 0
        else:
            return 1

    def _run_task_list(self) -> int:
        assert isinstance(self.task, KtrTaskList)

        code = 0
        for task in self.task.tasks:
            assert isinstance(task, KtrMetaTask)
            result = task.execute()

            if not result.success:
                code += 1

        return code

    def run(self) -> int:
        debugging = self.context.debug()

        if debugging:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        logfile = self.context.get_logfile()

        if logfile != "":
            logging.basicConfig(filename=logfile)

        if isinstance(self.task, KtrTaskList):
            return self._run_task_list()
        else:
            return self._run_task()
