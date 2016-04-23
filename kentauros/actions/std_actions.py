"""
This submodule contains the actions which are executed by the ``ktr`` CLI
script.
"""


from kentauros.definitions import ActionType

from kentauros.package import Package
from kentauros.actions.common import Action


class BuildAction(Action):
    """
    This :py:class:`Action` subclass contains information for executing a local
    build of the package specified at initialisation.

    Arguments:
        Package kpkg:       package this local build will done for
        bool force:         currently without effect (common flag of actions)

    Attributes:
        ActionType atype:   here: stores ``ActionType.BUILD``
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.BUILD

    def execute(self) -> bool:
        """
        This method runs the local build corresponding to the package specified
        at initialisation, with the configuration from package configuration
        file. This method executes the :py:meth:`kentauros.build.Builder.build`
        method of the Builder instance in the specified package.

        Returns:
            bool:   *True* if all builds were successful, *False* if otherwise
        """

        success = self.kpkg.builder.build()
        return success


class ChainAction(Action):
    """
    This `Action` subclass contains information for executing a "chain reaction"
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
        Package kpkg:       Package instance this chain reaction will done for
        bool force:         force further actions even if sources did not change

    Attributes:
        ActionType atype:   here: stores `ActionType.CHAIN`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.CHAIN

    def execute(self) -> bool:
        """
        This method runs the "chain reaction" corresponding to the package
        specified at initialisation, with the configuration from the package
        configuration file.

        Returns:
            bool:   *True* if chain went all the way through, *False* if not
        """

        verified = VerifyAction(self.kpkg, self.force).execute()
        if not verified:
            return False

        get = GetAction(self.kpkg, self.force).execute()
        update = UpdateAction(self.kpkg, self.force).execute()
        if not (get or update or self.force):
            return False

        ExportAction(self.kpkg, self.force).execute()

        success = ConstructAction(self.kpkg,
                                  self.force or get or update).execute()
        if not success:
            return False

        success = BuildAction(self.kpkg, self.force).execute()
        if not success:
            return False

        UploadAction(self.kpkg, self.force).execute()

        return True


class CleanAction(Action):
    """
    This `Action` subclass contains information for cleaning up the sources of
    the package specified at initialisation.

    Arguments:
        Package kpkg:       Package instance sources will be cleaned for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.CLEAN`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.CLEAN

    def execute(self) -> bool:
        """
        This method cleans up the sources of to the package specified at
        initialisation. It executes the :py:meth:`kentauros.source.Source.clean`
        method of the Source instance in the specified package.

        Returns:
            bool:           always *True* at the moment
        """

        self.kpkg.source.clean()
        return True


class ConstructAction(Action):
    """
    This `Action` subclass contains information for constructing the source
    package from sources and package specification for the package specified at
    initialisation.

    If `force=True` is specified, the build will succeed, even if the package
    version did not change, and will *not* reset the release number.

    If `force=True` is not specified (`force=False` by default), then the
    release number will only be reset if the package version changed between the
    last build and this one - otherwise it will be attempted to smartly
    increment the number.

    Arguments:
        Package kpkg:       Package instance source package will be built for
        bool force:         determines if release number will be bumped or not

    Attributes:
        ActionType atype:   here: stores `ActionType.CONSTRUCT`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.CONSTRUCT

    def execute(self) -> bool:
        """
        This method calls several :py:class:`kentauros.construct.Constructor`
        methods to execute the source package build.

        * `.init()`: general preparatory work (e.g. creating temporary dirs)
        * `.prepare()`: copy files to build directory, prepare build, increase
          release number, etc.
        * if the `.prepare()` stage is not successful, the action will terminate
        * `.build()`: build the source package inside the build directory
        * `.export()`: copy built source package to `$PACKAGEDIR`
        * `.clean()`: remove temporary build directory, if necessary

        Returns:
            bool:           *True* when successful, *False* if prepare failed
        """

        self.kpkg.constructor.init()

        success = self.kpkg.constructor.prepare(self.force)
        if not success:
            self.kpkg.constructor.clean()
            return False

        self.kpkg.constructor.build()
        self.kpkg.constructor.export()
        self.kpkg.constructor.clean()

        return True


class ExportAction(Action):
    """
    This `Action` subclass contains information for exporting the specified
    source from a VCS repository to a tarball (if necessary). It does not have
    any effect for local tarballs and tarballs specified by URL.

    Arguments:
        Package kpkg:       Package instance source export will be attempted for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.EXPORT`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.EXPORT

    def execute(self) -> bool:
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.export` method to execute the
        source export, if possible / necessary.

        Returns:
            bool:           *True* when successful, *False* if file exists
        """

        self.kpkg.source.export()
        return True


class GetAction(Action):
    """
    This `Action` subclass contains information for downloading or copying the
    package's source from the specified origin. Either a VCS repository will be
    cloned by the appropriate tool, or a tarball will be downloaded from URL,
    or a local copy will be made.

    Arguments:
        Package kpkg:       package source getting will be attempted for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.GET`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.GET

    def execute(self) -> bool:
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.get` method to execute the
        source download / copy, if possible / necessary.

        Returns:
            bool:           *True* when successful, *False* if action failed
        """

        return self.kpkg.source.get()


class PrepareAction(Action):
    """
    This `Action` subclass contains information for preparing the package's
    sources. Sources will be downloaded or copied to destination, updated if
    already there, and exported to a tarball, if necessary.

    Arguments:
        Package kpkg:       package for which source preparation is done
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.PREPARE`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.PREPARE

    def execute(self) -> bool:
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.prepare` method to execute
        source preparation. This includes downloading or copying to destination,
        updating if necessary, and exporting to tarball if necessary.

        Returns:
            bool:           *True* when successful, *False* if sub-action fails
        """

        return self.kpkg.source.prepare()


class RefreshAction(Action):
    """
    This `Action` subclass contains information for refreshing the package's
    source. Sources will be cleaned up and re-downloaded as specified.

    Arguments:
        Package kpkg:       Package instance for which source refreshing is done
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.REFRESH`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.REFRESH

    def execute(self) -> bool:
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.refresh` method to execute a
        source refresh. This includes cleaning up the package's source directory
        and redownloading or copying sources from origin to destination.

        Returns:
            bool:           *True* when successful, *False* if sub-action fails
        """

        return self.kpkg.source.refresh()


class StatusAction(Action):
    """
    This `Action` subclass contains information for displaying packages which
    are configured for use with kentauros. At the moment, this only includes
    printing a list of packages, which is done by default when kentauros is run.
    More status messages are plannned for the future.

    Arguments:
        Package kpkg:       Package instance for which status will be printed
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.STATUS`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.STATUS

    def execute(self) -> bool:
        """
        This method prints a pretty summary of a package's configuration values
        to the console.

        Currently, this does nothing whatsoever.
        """

        # TODO: output package configuration / status
        return True


class UpdateAction(Action):
    """
    This `Action` subclass contains information for updating the package's
    source as specified in the package configuration. This only has effect for
    VCS sources, which will pull upstream changes as specified.

    Arguments:
        Package kpkg:       Package instance source update will be run for
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.UPDATE`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.UPDATE

    def execute(self) -> bool:
        """
        This method executes the
        :py:meth:`kentauros.source.common.Source.update` method to execute the
        source updating, if possible - this only has effect for sources with
        an upstream VCS specified as origin.

        Returns:
            bool:   *True* when update was available, *False* if not or failure
        """

        update = self.kpkg.source.update()
        return update


class UploadAction(Action):
    """
    This `Action` subclass contains information for uploading the buildable
    source package to a cloud service (or similar) as specified in the package
    configuration.

    Arguments:
        Package kpkg:       source package upload will be done for `package`
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.UPLOAD`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.UPLOAD

    def execute(self) -> bool:
        """
        This method executes the
        :py:meth:`kentauros.upload.Uploader.upload` method to execute the
        source upload, if possible - this only has effect for packages with
        a valid uploader specified in the package configuration file.

        Returns:
            bool:           always *True*, future error checking still missing
        """

        # TODO: error handling
        self.kpkg.uploader.upload()
        return True


class VerifyAction(Action):
    """
    This `Action` subclass contains information for making sure the package's
    configuration file is valid and everything needed for actions is in place.

    Arguments:
        Package kpkg:       validation will be done for `package`
        bool force:         currently without effect

    Attributes:
        ActionType atype:   here: stores `ActionType.VERIFY`
    """

    def __init__(self, kpkg: Package, force: bool):
        super().__init__(kpkg, force)
        self.atype = ActionType.VERIFY

    def execute(self) -> bool:
        """
        This method executes a verification of the package configuration and
        checks if every file necessary for actions is present (and valid).

        Currently, this does no checking whatsoever.
        """

        # TODO: verify that package *.conf is valid
        return True

