"""
This subpackage contains the quasi-abstract :py:class:`Action` class and its
subclasses, which are used to hold information about the action specified at
command line and are used to execute their respective actions. Additionally,
this file contains a dictioary which maps
:py:class:`kentauros.definitions.ActionType` enums to their respective class
constructors.
"""

from configparser import ConfigParser, NoSectionError
import os
import shutil

from kentauros.definitions import KTR_SYSTEM_DATADIR, ActionType, SourceType
from kentauros.instance import Kentauros, log

from kentauros.package import Package


LOGPREFIX1 = "ktr/actions: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class Action:
    """
    This class is the base class for all defined actions. For every action that
    can be specified at ktr command line, there is an Action subclass.

    Arguments:
        package (Package): Package instance this action will be run on
        force (bool):      specifies if the pending action should be forced

    Attributes:
        package (Package): stores reference to `Package` given at initialisation
        force (bool): stores force value given at initialisation
        atype (ActionType): stores type of action as enum
    """

    def __init__(self, package, force):
        assert isinstance(package, Package)
        self.package = package

        self.force = force
        self.atype = None

    def execute(self):
        """
        This method runs the action corresponding to the Action instance on the
        package specified at initialisation. It is overridden by subclasses to
        contain the real code for the action. Here, it is only a dummy method
        that executes no code.

        Returns:
            bool: success of executed action
        """

        pass


class BuildAction(Action):
    """
    This Action subclass contains information for executing a local build of the
    package specified at initialisation.

    Arguments:
        Package package: Package instance this local build will done for
        bool force: (currently without effect)

    Attributes:
        atype (ActionType): here: stores `ActionType.BUILD`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.BUILD

    def execute(self):
        """
        This method runs the local build corresponding to the package specified
        at initialisation, with the configuration from package configuration
        file. This method executes the :py:meth:`kentauros.build.Builder.build`
        method of the Builder instance in the specified package.

        Returns:
            bool: *True* if all builds were successful, *False* if otherwise
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
      was not specified, action execution will terminate at this point and
      return `False`
    * otherwise, sources are exported (if tarball doesn't already exist)
      (`ExportAction`)
    * construct source package (`ConstructAction`), terminate chain if not
      successful
    * build source package locally (`BuildAction`), terminate chain if not
      successful
    * upload source package to cloud build service (`UploadAction`)

    Arguments:
        package (Package): Package instance this chain reaction will done for
        force (bool): force further actions even if sources did not change

    Attributes:
        atype (ActionType): here: stores `ActionType.CHAIN`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.CHAIN

    def execute(self):
        """
        This method runs the "chain reaction" corresponding to the package
        specified at initialisation, with the configuration from the package
        configuration file.

        Returns:
            bool: *True* if chain went all the way through, *False* if not
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
        package (Package): Package instance sources will be cleaned for
        force (bool): (currently without effect)

    Attributes:
        atype (ActionType): here: stores `ActionType.CLEAN`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.CLEAN

    def execute(self):
        """
        This method cleans up the sources of to the package specified at
        initialisation. It executes the :py:meth:`kentauros.source.Source.clean`
        method of the Source instance in the specified package.

        Returns:
            bool: always *True* at the moment
        """

        self.package.source.clean()
        return True


class ConfigAction(Action):
    """
    This Action subclass contains information for changing package configuration
    values stored in the package's \\*.conf file.

    Arguments:
        package (Package): Package instance configuration will be changed for
        force (bool): (currently without effect)
        section (str): section of conf file that `key` is in
        key (str): key that `value` will be written to
        value (str): value that will be set in configuration

    Attributes:
        atype (ActionType): here: stores `ActionType.CONFIG`
        section (str): stores `section` given at initialisation
        key (str): stores `key` given at initialisation
        value (str): stores `value` given at initialisation
    """

    def __init__(self, package, force, section, key, value):
        super().__init__(package, force)
        self.atype = ActionType.CONFIG

        self.section = section
        self.key = key
        self.value = value

    def execute(self):
        """
        This method checks if the specified section already exists in the
        configuration file - and creates it, if it doesn't. Following this
        check, it will change or add `section`/`key` to `value` in the
        :py:class:`configparser.ConfigParser` object and then writes the changed
        configuration back to the package's \\*.conf file.

        Returns:
            bool: always *True* at the moment
        """

        if self.section not in self.package.conf.sections():
            self.package.conf.add_section(self.section)

        self.package.conf.set(self.section, self.key, self.value)
        self.package.update_config()

        log(LOGPREFIX1 + "Configuration value changed: ", 2)
        log(LOGPREFIX1 + self.package.name + ".conf: " + \
            self.section + "/" + self.key + ": " + self.value, 2)

        return True


class ConstructAction(Action):
    """
    This Action subclass contains information for constructing the source
    package from sources and package specification for the package specified at
    initialisation.

    If `force=True` is specified, the build will succeed, even if the package
    version did not change, and will *not* reset the release number.

    If `force=True` is not specified (`force=False` by default), then the
    release number will only be reset if the package version changed between the
    last build and this one - otherwise it will be attempted to smartly
    increment the number.

    Arguments:
        package (Package): Package instance source package will be built for
        force (bool): determines if release number will be bumped or not

    Attributes:
        atype (ActionType): here: stores `ActionType.CONSTRUCT`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.CONSTRUCT

    def execute(self):
        """
        This method calls several :py:class:`kentauros.construct.Constructor`
        methods to execute the source package build.

        * `.init()`: general preparatory work (e.g. creating temporary dirs)
        * `.prepare()`: copy files to build directory, prepare build, increase
          release number, etc.
        * if the `.prepare()` stage is not successful, the action will terminate
        * `.build()`: build the source package inside the build directory
        * `.export()`: copy built source package to $PACKAGEDIR
        * `.clean()`: remove temporary build directory, if necessary

        Returns:
            bool: *True* when successful, *False* if preparation failed
        """

        self.package.constructor.init()

        success = self.package.constructor.prepare(relreset=(not self.force))
        if not success:
            self.package.constructor.clean()
            return False

        self.package.constructor.build()
        self.package.constructor.export()
        self.package.constructor.clean()

        return True


class ExportAction(Action):
    """
    This Action subclass contains information for exporting the specified source
    from a VCS repository to a tarball (if necessary). It does not have any
    effect for local tarballs and tarballs specified by URL.

    Arguments:
        package (Package): Package instance source export will be attempted for
        force (bool): (currently without effect)

    Attributes:
        atype (ActionType): here: stores `ActionType.EXPORT`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.EXPORT

    def execute(self):
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.export` method to execute the
        source export, if possible / necessary.

        Returns:
            bool: *True* when successful, *False* if export failed (file exists)
        """
        self.package.source.export()
        return True


class GetAction(Action):
    """
    This Action subclass contains information for downloading or copying the
    package's source from the specified origin. Either a VCS repository will be
    cloned by the appropriate tool, or a tarball will be downloaded from URL,
    or a local copy will be made.

    Arguments:
        package (Package): Package instance source getting will be attempted for
        force (bool): (currently without effect)

    Attributes:
        atype (ActionType): here: stores `ActionType.GET`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.GET

    def execute(self):
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.get` method to execute the
        source download / copy, if possible / necessary.

        Returns:
            bool: *True* when successful, *False* if action failed
        """
        return self.package.source.get()


class PrepareAction(Action):
    """
    This Action subclass contains information for preparing the package's
    source. Sources will be downloaded or copied to destination, updated if
    already there, and exported to a tarball, if necessary.

    Arguments:
        package (Package): Package instance for which source preparation is done
        force (bool): (currently without effect)

    Attributes:
        atype (ActionType): here: stores `ActionType.PREPARE`
    """

    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.PREPARE

    def execute(self):
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.prepare` method to execute
        source preparation. This includes downloading or copying to destination,
        updating if necessary, and exporting to tarball if necessary.

        Returns:
            bool: *True* when successful, *False* if any sub-action failed
        """
        return self.package.source.prepare()


class RefreshAction(Action):
    """
    kentauros.actions.RefreshAction:
    action for refreshing sources (clean + get)
    # TODO: write napoleon docstring
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.REFRESH

    def execute(self):
        # TODO: write napoleon docstring
        return self.package.source.refresh()


class StatusAction(Action):
    """
    kentauros.actions.StatusAction:
    action for displaying configuration values and available packages
    # TODO: write napoleon docstring
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.STATUS

    def execute(self):
        # TODO: write napoleon docstring
        # TODO: output package configuration / status
        return True


class UpdateAction(Action):
    """
    kentauros.actions.UpdateAction:
    action for updating sources
    # TODO: write napoleon docstring
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.UPDATE

    def execute(self):
        # TODO: write napoleon docstring
        update = self.package.source.update()
        return update


class UploadAction(Action):
    """
    kentauros.actions.UploadAction:
    action for uploading source package
    # TODO: write napoleon docstring
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.UPLOAD

    def execute(self):
        # TODO: write napoleon docstring
        self.package.uploader.upload()
        return True


class VerifyAction(Action):
    """
    kentauros.actions.VerifyAction:
    action for verifying that everything is in place
    # TODO: write napoleon docstring
    """
    def __init__(self, package, force):
        super().__init__(package, force)
        self.atype = ActionType.VERIFY

    def execute(self):
        # TODO: write napoleon docstring
        # TODO: verify that package *.conf is valid
        return True


class CreateAction:
    """
    kentauros.actions.CreateAction:
    action for initialising an empty package from templates
    # TODO: write napoleon docstring
    """
    def __init__(self, name, force):
        assert isinstance(name, str)
        self.name = name
        self.force = force

    def execute(self):
        """
        # TODO: write napoleon docstring
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
            log(LOGPREFIX1 + self.name + \
                ".conf already exists. Specify --force to overwrite.", 2)
            success = False

        if not os.path.exists(spec_template_dest) or self.force:
            shutil.copy2(spec_template_orig, spec_template_dest)
        else:
            log(LOGPREFIX1 + self.name + \
                ".spec already exists. Specify --force to overwrite.", 2)
            success = False

        if success:
            # set name in config template
            conf_template = ConfigParser()
            conf_template.read(conf_template_dest)

            conf_template.set("package", "name", self.name)
            conf_template.write(conf_template_dest)

        return success


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

