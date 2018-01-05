import os

from .meta import KtrMetaTask

from ..context import KtrContext
from ..result import KtrResult
from ..templates import PACKAGE_CONF_TEMPLATE


class KtrPackageAddTask(KtrMetaTask):
    def __init__(self, conf_name: str, context: KtrContext):
        self.conf_name = conf_name
        self.context = context

    def execute(self) -> KtrResult:
        ret = KtrResult(True)

        path = os.path.join(self.context.get_confdir(), self.conf_name + ".conf")

        try:
            with open(path, "w") as file:
                file.write(PACKAGE_CONF_TEMPLATE)
        except OSError:
            ret.messages.log(
                "Package .conf file for package '{}' could not be created.".format(self.conf_name))
            ret.success = False

        return ret
