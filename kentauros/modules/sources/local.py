import os
import shutil

from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult
from ...validator import KtrValidator

from .abstract import Source


class LocalSource(Source):
    NAME = "Local Source"

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)

        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.stype = "local"

    def __str__(self) -> str:
        return "Local Source for Package '" + self.package.conf_name + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        # check if the configuration file is valid
        expected_keys = ["keep", "orig"]
        validator = KtrValidator(self.package.conf.conf, "local", expected_keys)

        return validator.validate()

    def get_keep(self) -> bool:
        return self.package.conf.getboolean("local", "keep")

    def get_orig(self) -> str:
        return self.package.replace_vars(self.package.conf.get("local", "orig"))

    def status(self) -> KtrResult:
        return KtrResult(True)

    def status_string(self) -> KtrResult:
        return KtrResult(True, "")

    def imports(self) -> KtrResult:
        return KtrResult(True)

    def get(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            ret.messages.log("Sources already present.")
            return ret.submit(False)

        # copy file from origin to destination
        shutil.copy2(self.get_orig(), self.dest)

        ret.state["source_files"] = [os.path.basename(self.get_orig())]
        return ret.submit(True)

    def export(self) -> KtrResult:
        return KtrResult(True)

    def update(self) -> KtrResult:
        return KtrResult(True)
