"""
This module contains the template / dummy :py:class:`Source` class, which is then inherited by
actual sources.
"""


import abc
import os
import shutil

from ...context import KtrContext
from ...package import KtrPackage
from ...result import KtrResult

from ..module import KtrModule


class Source(KtrModule, metaclass=abc.ABCMeta):
    """
    This class serves as an abstract base class for source handlers. They are expected to override
    this class's unimplemented methods. It also provides common infrastructure for all code sources
    in the form of generalised implementations of `get`, `refresh` and `formatver` methods.

    Attributes:
        bool updated:       indicates whether the source was updated since the state in the DB
        str sdir:           source directory of the package this source belongs to
        str dest:           destination path when downloading / copying sources
        Package spkg:       stores the package argument given at initialisation
        SourceType stype:   type of source
    """

    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.updated = False

        self.sdir = os.path.join(self.context.get_datadir(), self.package.conf_name)

        self.dest = None
        self.stype = None

        self.actions["export"] = self.export
        self.actions["get"] = self.get
        self.actions["prepare"] = self.execute
        self.actions["refresh"] = self.refresh
        self.actions["update"] = self.update

    @abc.abstractmethod
    def get_orig(self) -> str:
        """
        This method is expected to read and return the 'orig' value specified in the package
        configuration file in the source section. It is also expected to replace variables with
        their corresponding values.
        """

    @abc.abstractmethod
    def get_keep(self) -> bool:
        """
        This method is expected to read and return the 'keep' value specified in the package
        configuration file in the source section.
        """

    @abc.abstractmethod
    def export(self) -> KtrResult:
        """
        It is expected that an appropriately named tarball is present within the package's source
        directory after this method has been executed.
        """

    @abc.abstractmethod
    def get(self) -> KtrResult:
        """
        It is expected that an appropriately named source file or directory is present within the
        package's source directory after this method has been executed.
        """

    @abc.abstractmethod
    def update(self) -> KtrResult:
        """
        It is expected that the source repository present within the package's source directory is
        up-to-date with upstream sources after this method has been executed, except when package
        configuration explicitely specifies something else.
        """

    @abc.abstractmethod
    def status(self) -> KtrResult:
        """
        This method is expected to return a dictionary of statistics about the respective source.
        This might include, for example, the current git commit hash, bzr revision number, etc.
        """

    def clean(self) -> KtrResult:
        """
        This method cleans up all of a package's sources - excluding other files in the packages's
        source directory, which may include patches or other, additional files - they are preserved.

        Returns:
            bool:   *True* if successful
        """

        ret = KtrResult(name=self.name())

        if not os.path.exists(self.sdir):
            ret.messages.log("Nothing here to be cleaned.")
            return ret.submit(True)

        # try to be careful with "rm -r"
        try:
            assert os.path.isabs(self.dest)
            assert self.context.get_datadir() in self.dest
        except AssertionError as error:
            ret.messages.log("Source directory looked suspicious, not recursively deleting. Error:")
            ret.messages.log(str(error))
            ret.submit(False)

        # remove source destination first

        # if destination is a file (tarball):
        if os.path.isfile(self.dest):
            os.remove(self.dest)

        # if destination is a directory (VCS repo):
        elif os.path.isdir(self.dest):
            shutil.rmtree(self.dest)

        # if source directory is empty now (no patches, additional files, etc. left):
        # remove whole directory
        if not os.listdir(self.sdir):
            os.rmdir(self.sdir)

        return ret.submit(True)

    def formatver(self) -> KtrResult:
        """
        This method provides a generic way of getting a package's version as string. Subclasses are
        expected to override this method with their own version string generators, which then might
        include git commit hashes, git commit date and time, bzr revision, etc..

        Returns:
            str:        formatted version string
        """

        ret = KtrResult(name=self.name())

        version_format = self.package.conf.get("source", "version")

        ret.value = version_format
        ret.state["version_format"] = version_format
        return ret.submit(True)

    def execute(self) -> KtrResult:
        """
        This method provides a generic way of preparing a package's sources. This will invoke the
        :py:meth:`Source.get()` method or the :py:meth:`Source.update()` method and the
        :py:meth:`Source.export()` method (as overridden by the subclass, respectively).

        If sources can be downloaded / copied into place successfully, an update for them will not
        be attempted. Otherwise (sources are already present within the package directory), an
        update will be attempted before exporting.

        Returns:
            bool:       success status of source getting or updating
        """

        ret = KtrResult(name=self.name())

        force = self.context.get_argument("force")
        old_status = self.status()

        res = self.get()
        ret.collect(res)

        if res.success:
            new_status = self.status()

            if new_status == old_status:
                ret.messages.log(
                    "The downloaded Source is not newer than the last known source state.")
                return ret.submit(False)
            else:
                self.updated = True
                res = self.export()
                ret.collect(res)
                return res.submit(res.success)

        res = self.update()
        ret.collect(res)

        if res.success:
            new_status = self.status()

            if new_status == old_status:
                ret.messages.log(
                    "The \"updated\" Source is not newer than the last known source state.")
                return ret.submit(False)
            else:
                self.updated = True
                res = self.export()
                ret.collect(res)
                return ret.submit(res.success)

        if force:
            ret.messages.log("Force-Exporting the Sources despite no source changes.")
            res = self.export()
            ret.collect(res)
            return ret.submit(res.success)

        ret.messages.log("The Source did not change.")
        return ret.submit(False)

    def refresh(self) -> KtrResult:
        """
        This method provides a generic way of refreshing a package's sources. This will invoke the
        generic :py:meth:`Source.clean()` method and the :py:meth:`Source.get()` method (as
        overridden by the subclass).

        Returns:
            bool:       success status of source getting
        """

        ret = KtrResult(name=self.name())

        res = self.clean()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Source cleanup not successful. Not getting sources again.")
            return ret.submit(False)

        res = self.get()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Source getting not successful.")
            return ret.submit(False)

        # everything successful:
        return ret.submit(True)
