"""
This submodule contains the :py:class:`CreateAction`, which is executed by the
``ktr-create`` CLI script.
"""


from configparser import ConfigParser

import os
import shutil

from kentauros.definitions import KTR_SYSTEM_DATADIR, ActionType
from kentauros.instance import Kentauros, log

from kentauros.actions.action import LOGPREFIX1


class CreateAction:
    """
    This action is the only one that is not an :py:class:`Action` subclass,
    because a non-existing package cannot be supplied as an argument. Instead,
    this class takes a name string as argument at initialisation, and creates
    all files needed for a valid package configuration from templates.

    Arguments:
        str name:           name of the package that will be created
        bool force:         currently without effect (common flag of actions)

    Attributes:
        ActionType atype:   here: stores ``ActionType.CREATE``
    """

    def __init__(self, name: str, force: bool):
        assert isinstance(name, str)
        assert isinstance(force, bool)

        self.atype = ActionType.CREATE

        self.name = name
        self.force = force


    def execute(self) -> bool:
        """
        This method copies the template package configuration file and template
        specification file to the future package's configuration and template
        file location. At the moment, the specification template is only
        available as a simple RPM spec template.

        Returns:
            bool:   ``True`` if everything was copied into place successfully
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

