"""
This sub-module contains only contains the :py:class:`LocalSource` class, which has methods for
handling sources that have `source.type=local` specified and `source.orig` set to an absolute path
of a local file in the package's configuration file.
"""


import os
import shutil

from ...definitions import SourceType
from ...logcollector import LogCollector
from ...result import KtrResult

from .abstract import Source


class LocalSource(Source):
    """
    This :py:class:`Source` subclass provides handling of local sources.

    Arguments:
        Package package:    package instance this source belongs to
    """

    NAME = "Local Source"

    def __init__(self, package):
        super().__init__(package)

        self.dest = os.path.join(self.sdir, os.path.basename(self.get_orig()))
        self.stype = SourceType.LOCAL

    def __str__(self) -> str:
        return "Local Source for Package '" + self.spkg.get_conf_name() + "'"

    def name(self):
        return self.NAME

    def verify(self) -> KtrResult:
        """
        This method runs several checks to ensure local copying can proceed. It is automatically
        executed at package initialisation. This includes:

        * checks if all expected keys are present in the configuration file

        Returns:
            bool:   verification success
        """

        logger = LogCollector(self.name())

        success = True

        # check if the configuration file is valid
        expected_keys = ["keep", "orig"]

        for key in expected_keys:
            if key not in self.spkg.conf["local"]:
                logger.err("The [local] section in the package's .conf file doesn't set the '" +
                           key +
                           "' key.")
                success = False

        return KtrResult(success, logger)

    def get_keep(self) -> bool:
        return self.spkg.conf.getboolean("local", "keep")

    def get_orig(self) -> str:
        """
        Returns:
            str:    string containing the source file path
        """

        return self.spkg.replace_vars(self.spkg.conf.get("local", "orig"))

    def status(self) -> dict:
        return dict()

    def status_string(self) -> str:
        return str()

    def imports(self) -> dict:
        return dict()

    def get(self) -> KtrResult:
        """
        This method attempts to copy the specified source from the location specified in the package
        configuration file to the determined destination. If the destination file already exists,
        nothing will be done.

        Returns:
            bool:   *True* if source was copied successfully, *False* if not
        """

        logger = LogCollector(self.name())

        # check if $KTR_BASE_DIR/sources/$PACKAGE exists and create if not
        if not os.access(self.sdir, os.W_OK):
            os.makedirs(self.sdir)

        # if source seems to already exist, return False
        if os.access(self.dest, os.R_OK):
            logger.log("Sources already present.")
            return KtrResult(False, logger)

        # copy file from origin to destination
        shutil.copy2(self.get_orig(), self.dest)

        return KtrResult(True, logger)

    def export(self) -> KtrResult:
        return KtrResult.true()

    def update(self) -> KtrResult:
        return KtrResult.true()
