import os

from .abstract import Source
from ...conntest import is_connected
from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...shellcmd import ShellCommand
from ...validator import KtrValidator


class WGetCommand(ShellCommand):
    NAME = "wget Command"

    def __init__(self, *args, path: str = None, binary: str = None):
        if binary is None:
            self.exec = "wget"
        else:
            self.exec = binary

        if path is None:
            path = os.getcwd()

        super().__init__(path, self.exec, *args)


class UrlSource(Source):
    NAME = "URL Source"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.stype = "url"

        state = self.context.state.read(self.package.conf_name)

        if state is None:
            self.last_version = None
        elif "url_last_version" in state:
            self.last_version = state["url_last_version"]
        else:
            self.last_version = None

    def __str__(self) -> str:
        return "URL Source for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        expected_keys = ["keep", "orig"]
        expected_binaries = ["wget"]

        validator = KtrValidator(self.package.conf.conf, "url", expected_keys, expected_binaries)

        return validator.validate()

    def get_keep(self) -> bool:
        return self.package.conf.getboolean("url", "keep")

    def get_orig(self) -> str:
        return self.package.replace_vars(self.package.conf.get("url", "orig"))

    def status(self) -> KtrResult:
        if self.last_version is None:
            return KtrResult(True)
        else:
            state = dict(url_last_version=self.last_version)
            return KtrResult(True, state=state)

    def status_string(self) -> KtrResult:
        state = self.context.state.read(self.package.conf_name)

        if "url_last_version" in state:
            string = ("url source module:\n" +
                      "  Last download:    {}\n".format(state["url_last_version"]))
        else:
            string = ("url source module:\n" +
                      "  Last download:    None\n")

        return KtrResult(True, string, state=state)

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            return KtrResult(True, state=dict(url_last_version=self.package.get_version()))
        else:
            return KtrResult(True)

    def get(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            ret.messages.log("Sources already downloaded.")
            return ret.submit(True)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            ret.messages.log("No connection to remote host detected. Cancelling source download.")
            return ret.submit(False)

        # construct wget commands
        cmd = ["wget", self.get_orig(), "-O", self.dest]

        res = WGetCommand(*cmd).execute()
        ret.collect(res)

        if not res.success:
            ret.messages.lst("Sources could not be downloaded successfully. CLI output:", res.value)
            return ret.submit(False)

        self.last_version = self.package.get_version()
        ret.state["source_files"] = [os.path.basename(self.get_orig())]

        return ret.submit(True)

    def update(self) -> KtrResult:
        ret = KtrResult(True, name=self.name())
        ret.messages.log("URL sources don't need to be updated.")
        return ret

    def export(self) -> KtrResult:
        ret = KtrResult(True, name=self.name())
        ret.messages.log("URL sources don't need to be exported.")
        return ret
