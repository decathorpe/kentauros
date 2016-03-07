"""
kentauros.actions module
classes, methods, functions, definitions for actions executable by CLI arguments
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
    kentauros.actions.Action:
    base class for Actions that are chosen by CLI
    """
    def __init__(self, package, force):
        assert isinstance(package, Package)
        self.package = package

        self.force = force
        self.type = None

    def execute(self):
        """
        kentauros.actions.Action.execute:
        execute Action
        """
        # pylint: disable=no-self-use
        return True


class BuildAction(Action):
    """
    kentauros.actions.BuildAction:
    action for building source package locally
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.BUILD

    def execute(self):
        success = self.package.builder.build()
        return success


class ChainAction(Action):
    """
    kentauros.actions.ChainAction:
    action for getting (if neccessary), updating, constructing,
    building and uploading source package
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.CHAIN

    def execute(self):
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
    kentauros.actions.Clean:
    action for cleaning sources
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.type = ActionType.CLEAN

    def execute(self):
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
            log(LOGPREFIX1 + name + ".conf already exists. Specify --force to overwrite.", 2)
            self.success = False

        if not os.path.exists(spec_template_dest) or force:
            shutil.copy2(spec_template_orig, spec_template_dest)
        else:
            log(LOGPREFIX1 + name + ".spec already exists. Specify --force to overwrite.", 2)
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

