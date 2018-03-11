import logging
import os

from kentauros.conntest import is_connected
from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from kentauros.result import KtrResult
from kentauros.shell_env import ShellEnv
from kentauros.validator import KtrValidator
from .abstract import Source

URL_STATUS_TEMPLATE = """
URL source module:
  Last version:     {download}
"""


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

        self._logger = logging.getLogger("ktr/sources/url")

    def __str__(self) -> str:
        return "URL Source for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    @property
    def logger(self):
        return self._logger

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
        ret = KtrResult()

        state = self.context.state.read(self.package.conf_name)

        if "url_last_version" in state:
            last_version = state["url_last_version"]
        else:
            last_version = "None"

        self.logger.info(URL_STATUS_TEMPLATE.format(download=last_version))

        return ret

    def imports(self) -> KtrResult:
        if os.path.exists(self.dest):
            return KtrResult(True, state=dict(url_last_version=self.package.get_version()))
        else:
            return KtrResult(True)

    def get(self) -> KtrResult:
        ret = KtrResult()

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            self.logger.info("Sources already downloaded.")
            return ret.submit(True)

        # check for connectivity to server
        if not is_connected(self.get_orig()):
            self.logger.error("No connection to remote host detected. Cancelling source download.")
            return ret.submit(False)

        # construct wget commands
        cmd = ["wget", self.get_orig(), "-O", self.dest]

        with ShellEnv() as env:
            res = env.execute(*cmd)
        ret.collect(res)

        if not res.success:
            self.logger.error("Sources could not be downloaded successfully:")
            self.logger.error(res.value)
            return ret.submit(False)

        self.last_version = self.package.get_version()
        ret.state["source_files"] = [os.path.basename(self.get_orig())]

        return ret.submit(True)

    def update(self) -> KtrResult:
        ret = KtrResult()
        self.logger.info("URL sources don't need to be updated.")
        return ret.submit(True)

    def export(self) -> KtrResult:
        ret = KtrResult()
        self.logger.info("URL sources don't need to be exported.")
        return ret.submit(True)
