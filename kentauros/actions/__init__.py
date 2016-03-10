"""
This module contains the quasi-abstract Action class and its subclasses, that
are used to hold information about actions specified at command line and are
used to execute their respective actions.
"""

from configparser import ConfigParser, NoSectionError
import os
import shutil

from kentauros.config import KTR_CONF
from kentauros.definitions import KTR_SYSTEM_DATADIR, ActionType, SourceType
from kentauros.init import log
from kentauros.package import Package


LOGPREFIX1 = "ktr/actions: "


class Action:
    """
    This class is the base class for all defined actions. For every action that
    can be specified at ktr command line, there is an Action subclass.

    Arguments:
        package (Package): Package instance this action will be run on
        force (bool):      specifies if the pending action should be forced

    Attributes:
        package (Package): stores reference to `Package` given at initialisation
        force (bool):      stores force value given at initialisation
        type (ActionType): stores type of action as enum
    """

    def __init__(self, package, force):
        assert isinstance(package, Package)
        self.package = package

        self.force = force
        self.type = None

    def execute(self):
        """
        This method runs the action corresponding to the Action instance on the
        package specified at initialisation. It is overridden by subclasses to
        contain the real code for the action. Here, it is only a dummy method
        that executes no code.

        Returns:
            bool:   success of executed action
        """

        pass


class BuildAction(Action):
    """
    This Action subclass contains information for executing a local build of the
    package specified at initialisation.

    Arguments:
        Package package:    Package instance this local build will done for
        bool force:         (currently without effect)
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.BUILD

    def execute(self):
        """
        This method runs the local build corresponding to the package specified
        at initialisation, with the configuration from package configuration
        file. This method executes the :py:meth:`kentauros.build.Builder.build`
        method of the Builder instance in the specified package.

        Returns:
            bool:   *True* if all builds were successful, *False* if otherwise
        """

        success = self.package.builder.build()
        return success


class ChainAction(Action):
    """
    This Action subclass contains information for executing a "chain reaction"
    on the package specified at initialisation, which means the following:

    * get sources if they don't already exist (`GetAction`)
    * update sources (`UpdateAction`)
    * if sources already existed, no updates were available and `force`
      was not specified, action execution will terminate at this point
    * otherwise, sources are exported (if tarball doesn't already exist)
      (`ExportAction`)
    * construct source package (`ConstructAction`), abort if unsuccessful
    * build source package locally (`BuildAction`), abort if unsuccessful
    * upload source package to cloud build service (`UploadAction`)

    Arguments:
        Package package:    Package instance this local build will done for
        bool force:         force further actions even if sources did not change
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.CHAIN

    def execute(self):
        """
        This method runs the "chain reaction" corresponding to the package
        specified at initialisation, with the configuration from package
        configuration file.

        Returns:
            bool:   *True* if chain went all the way through, *False* if not
        """

        veryfied = VerifyAction(self.package, self.force).execute()
        if not veryfied:
            return False

        get = GetAction(self.package, self.force).execute()
        update = UpdateAction(self.package, self.force).execute()
        if not (get or update or self.force):
            return False

        ExportAction(self.package, self.force).execute()

        success = ConstructAction(self.package, self.force).execute()
        if not success:
            return False

        success = BuildAction(self.package, self.force).execute()
        if not success:
            return False

        UploadAction(self.package, self.force).execute()

        return True


class CleanAction(Action):
    """
    This Action subclass contains information for cleaning up the sources of the
    package specified at initialisation.

    Arguments:
        Package package:    Package instance sources will be cleaned for
        bool force:         (currently without effect)
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.CLEAN

    def execute(self):
        """
        This method cleans up the sources of to the package specified at
        initialisation. It executes the :py:meth:`kentauros.source.Source.clean`
        method of the Source instance in the specified package.

        Returns:
            bool:   always *True* at the moment
        """

        self.package.source.clean()
        return True


class ConfigAction(Action):
    """
    kentauros.actions.ConfigAction:
    action for setting config values
    """
    def __init__(self, package, force, section, key, value):
        super().__init__(package, force)
        self.type = ActionType.CONFIG

        self.section = section
        self.key = key
        self.value = value

    def execute(self):
        try:
            self.package.conf.set(self.section, self.key, self.value)
        except NoSectionError:
            return False

        self.package.update_config()

        log(LOGPREFIX1 + "Configuration value changed: ", 2)
        log(LOGPREFIX1 + self.package.name + ".conf: " + \
            self.section + "/" + self.key + ": " + self.value, 2)

        return True


class ConstructAction(Action):
    """
    kentauros.actions.Construct:
    action for building source package
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.CONSTRUCT

    def execute(self):
        self.package.constructor.init()

        success = self.package.constructor.prepare(relreset=(not self.force))
        if not success:
            return False

        self.package.constructor.build()
        self.package.constructor.export()
        self.package.constructor.clean()

        return True


class CreateAction(Action):
    """
    kentauros.actions.CreateAction:
    action for initialising an empty package from templates
    """
    def __init__(self, name, force):
        assert isinstance(name, str)

        # copy templates from KTR_SYSTEM_DATADIR to confdir and specdir
        conf_template_orig = os.path.join(KTR_SYSTEM_DATADIR, "package.conf")
        spec_template_orig = os.path.join(KTR_SYSTEM_DATADIR, "template.spec")

        conf_template_dest = os.path.join(KTR_CONF.confdir, name + ".conf")
        spec_template_dest = os.path.join(KTR_CONF.specdir, name + ".spec")

        self.success = True

        if not os.path.exists(conf_template_dest) or force:
            shutil.copy2(conf_template_orig, conf_template_dest)
        else:
            log(LOGPREFIX1 + name + \
                ".conf already exists. Specify --force to overwrite.", 2)
            self.success = False

        if not os.path.exists(spec_template_dest) or force:
            shutil.copy2(spec_template_orig, spec_template_dest)
        else:
            log(LOGPREFIX1 + name + \
                ".spec already exists. Specify --force to overwrite.", 2)
            self.success = False

        if self.success:
            # set name in config template
            conf_template = ConfigParser()
            conf_template.read(conf_template_dest)

            conf_template.set("package", "name", name)
            conf_template.write(conf_template_dest)

            # initialise package
            package = Package(name)
            super().__init__(package, force)

    def execute(self):
        return self.success


class ExportAction(Action):
    """
    kentauros.actions.ExportAction:
    action for exporting sources from repository
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.EXPORT

    def execute(self):
        self.package.source.export()
        return True


class GetAction(Action):
    """
    kentauros.actions.GetAction:
    action for getting sources
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.GET

    def execute(self):
        return self.package.source.get()


class PrepareAction(Action):
    """
    kentauros.actions.PrepareAction:
    action for preparing sources (get/update, export)
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.PREPARE

    def execute(self):
        return self.package.source.prepare()


class RefreshAction(Action):
    """
    kentauros.actions.RefreshAction:
    action for refreshing sources (clean + get)
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.REFRESH

    def execute(self):
        self.package.source.refresh()
        # TODO
        # Source.refresh() needs return value from .get()
        return True


class StatusAction(Action):
    """
    kentauros.actions.StatusAction:
    action for displaying configuration values and available packages
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.STATUS

    def execute(self):
        # TODO
        return True


class UpdateAction(Action):
    """
    kentauros.actions.UpdateAction:
    action for updating sources
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.UPDATE

    def execute(self):
        update = self.package.source.update()
        return update


class UploadAction(Action):
    """
    kentauros.actions.UploadAction:
    action for uploading source package
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.UPLOAD

    def execute(self):
        self.package.uploader.upload()
        return True


class VerifyAction(Action):
    """
    kentauros.actions.VerifyAction:
    action for verifying that everything is in place
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.VERIFY

    def execute(self):
        # TODO
        return True


ACTION_DICT = dict()
ACTION_DICT[ActionType.BUILD] = BuildAction
ACTION_DICT[ActionType.CHAIN] = ChainAction
ACTION_DICT[ActionType.CLEAN] = CleanAction
ACTION_DICT[ActionType.CONFIG] = ConfigAction
ACTION_DICT[ActionType.CONSTRUCT] = ConstructAction
ACTION_DICT[ActionType.CREATE] = CreateAction
ACTION_DICT[ActionType.EXPORT] = ExportAction
ACTION_DICT[ActionType.GET] = GetAction
ACTION_DICT[ActionType.PREPARE] = PrepareAction
ACTION_DICT[ActionType.REFRESH] = RefreshAction
ACTION_DICT[ActionType.STATUS] = StatusAction
ACTION_DICT[ActionType.UPDATE] = UpdateAction
ACTION_DICT[ActionType.UPLOAD] = UploadAction
ACTION_DICT[ActionType.VERIFY] = VerifyAction

