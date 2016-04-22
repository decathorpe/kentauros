"""
This submodule contains the actions used by a invocation of the `ktr-create`
script.
"""


from configparser import ConfigParser

import os
import shutil

from kentauros.definitions import KTR_SYSTEM_DATADIR
from kentauros.instance import Kentauros, log

from kentauros.actions.common import LOGPREFIX1


class CreateAction:
    """
    This `Action` subclass contains information for making sure the package's
    configuration file is valid and everything needed for actions is in place.

    Arguments:
        str name:           validation will be done for `package`
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.VERIFY`
    """

    def __init__(self, name: str, force: bool):
        assert isinstance(name, str)
        assert isinstance(force, bool)

        self.name = name
        self.force = force

    def execute(self) -> bool:
        """
        This method copies the template package configuration file and template
        specification file to the future package's configuration and template
        file location. At the moment, the specification template is only
        available as a simple RPM spec template.

        Returns:
            bool:       *True* if everything was copied into place successfully
        """

        # copy templates from KTR_SYSTEM_DATADIR to confdir and specdir
        conf_template_orig = os.path.join(KTR_SYSTEM_DATADIR, "package.conf")
        spec_template_orig = os.path.join(KTR_SYSTEM_DATADIR, "template.spec")

        ktr = Kentauros()

        conf_template_dest = os.path.join(
            ktr.conf.confdir, self.name + ".conf")
        spec_template_dest = os.path.join(
            ktr.conf.specdir, self.name + ".spec")

        success = True

        if not os.path.exists(conf_template_dest) or self.force:
            shutil.copy2(conf_template_orig, conf_template_dest)
        else:
            log(LOGPREFIX1 + self.name +
                ".conf already exists. Specify --force to overwrite.", 2)
            success = False

        if not os.path.exists(spec_template_dest) or self.force:
            shutil.copy2(spec_template_orig, spec_template_dest)
        else:
            log(LOGPREFIX1 + self.name +
                ".spec already exists. Specify --force to overwrite.", 2)
            success = False

        if success:
            # set name in config template
            conf_template = ConfigParser()
            conf_template.read(conf_template_dest)

            conf_template.set("package", "name", self.name)
            conf_template.write(conf_template_dest)

        return success

