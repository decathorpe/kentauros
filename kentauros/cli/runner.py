from ..modules import get_module
from ..package import KtrPackage
from ..tasks import KtrTask, KtrInitTask, KtrTaskList, KtrPackageTask

from .context import KtrCLIContext


class KtrCLIRunner:
    def __init__(self):
        self.context = KtrCLIContext()

        conf_names = self.context.get_packages()
        module_type = self.context.get_module()

        if module_type == "init":
            self.task = KtrInitTask(self.context)

        elif module_type == "package":
            action = self.context.get_module_action()

            for conf_name in conf_names:
                package = KtrPackage(self.context, conf_name)
                self.task = KtrPackageTask(package, action, self.context)
        else:
            action = self.context.get_module_action()
            self.task: KtrTaskList = KtrTaskList()

            for conf_name in conf_names:
                package = KtrPackage(self.context, conf_name)
                module_impl = package.conf.get("modules", module_type)
                module = get_module(module_type, module_impl, package, self.context)
                task = KtrTask(package, module, action, self.context)

                self.task.add(task)

    def run(self) -> int:
        result = self.task.execute()

        logfile = self.context.get_argument("logfile")
        warnings = self.context.warnings()
        debug = self.context.debug()

        if not logfile:
            result.messages.print(warnings, debug)
        else:
            with open(logfile, "a") as file:
                result.messages.print(dest=file, warnings=warnings, debug=debug)

        if result.success:
            return 0
        else:
            return -1
