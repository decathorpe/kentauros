"""
This submodule contains the :py:class:`ConstructAction` class.
"""


from kentauros.definitions import ActionType

from kentauros.logger import KtrLogger

from kentauros.actions.abstract import Action
from kentauros.actions.common import LOGPREFIX


class ConstructAction(Action):
    """
    This :py:class:`Action` subclass contains information for constructing the source package from
    sources and package specification for the package specified at initialisation.

    If ``force=True`` is specified, the build will continue, even if the package version did not
    change, and the package release number will *not* be reset, but smartly incremented (e. g. for
    packaging related changes).

    If ``force=False`` is specified (the default), then the package construction will only continue
    if the version in the package configuration file differs from the version in the spec file
    (major version update), or if VCS sources had been updated. If package construction is executed,
    the release number will be reset to 0 and a changelog entry will be added for the new version.

    Arguments:
        str pkg_name:       Package name for which status will be printed

    Attributes:
        ActionType atype:   here: stores ``ActionType.CONSTRUCT``
    """

    def __init__(self, pkg_name: str):
        super().__init__(pkg_name)
        self.atype = ActionType.CONSTRUCT

    def execute(self) -> bool:
        """
        This method calls several :py:class:`Constructor` methods to execute the source package
        build.

        - initialisation (:py:meth:`Constructor.init()`): general preparatory work (e.g. creating
          temporary dirs)
        - preparation (:py:meth:`Constructor.prepare()`): copy files to build directory, prepare
          build, determine version, release number, etc.
        - if the preparation stage is not successful, the action will terminate
        - construction (:py:meth:`Constructor.build()`): build the source package inside the build
          directory
        - export (:py:meth:`Constructor.export()`): copy the built source package to the kentauros
          package directory
        - cleanup (:py:meth:`Constructor.clean()`): remove temporary build directory and/or files
          (if necessary)

        Returns:
            bool:       ``True`` when successful, ``False`` if an error occurred
        """

        constructor = self.kpkg.get_module("constructor")

        constructor.init()

        success = constructor.prepare()
        if not success:
            constructor.clean()
            KtrLogger(LOGPREFIX).log("Source package assembly unsuccessful.", 2)
            return False

        constructor.build()
        constructor.export()
        constructor.clean()

        return True
