"""
This module contains the template / dummy :py:class:`Source` class, which is then inherited by
actual sources.
"""


import abc
import os
import shutil

from kentauros.instance import Kentauros
from kentauros.logger import KtrLogger
from kentauros.modules.module import PkgModule


LOGPREFIX = "ktr/sources"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class Source(PkgModule, metaclass=abc.ABCMeta):
    """
    This class serves as an abstract base class for source handlers. They are expected to override
    this class's unimplemented methods. It also provides common infrastructure for all code sources
    in the form of generalised implementations of get, refresh and formatver methods.

    Attributes:
        str sdir:           source directory of the package this source belongs to
        str dest:           destination path when downloading / copying sources
        Package spkg:       stores the package argument given at initialisation
        SourceType stype:   type of source
    """

    def __init__(self, package):
        ktr = Kentauros()

        if ktr.debug:
            from kentauros.package import Package
            assert isinstance(package, Package)

        self.spkg = package
        self.sdir = os.path.join(ktr.conf.get_datadir(), self.spkg.get_conf_name())

        self.dest = None
        self.stype = None

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
    def export(self):
        """
        It is expected that an appropriately named tarball is present within the package's source
        directory after this method has been executed.
        """

    @abc.abstractmethod
    def get(self):
        """
        It is expected that an appropriately named source file or directory is present within the
        package's source directory after this method has been executed.
        """

    @abc.abstractmethod
    def update(self):
        """
        It is expected that the source repository present within the package's source directory is
        up-to-date with upstream sources after this method has been executed, except when package
        configuration explicitely specifies something else.
        """

    @abc.abstractmethod
    def status(self) -> dict:
        """
        This method is expected to return a dictionary of statistics about the respective source.
        This might include, for example, the current git commit hash, bzr revision number, etc.
        """

    def clean(self) -> bool:
        """
        This method cleans up all of a package's sources - excluding other files in the packages's
        source directory, which may include patches or other, additional files - they are preserved.

        Returns:
            bool:   *True* if successful
        """

        ktr = Kentauros()
        logger = KtrLogger(LOGPREFIX)

        if not os.path.exists(self.sdir):
            logger.log("Nothing here to be cleaned.", 0)
            return True

        # try to be careful with "rm -r"
        assert os.path.isabs(self.dest)
        assert ktr.conf.get_datadir() in self.dest

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

        return True

    def formatver(self) -> str:
        """
        This method provides a generic way of getting a package's version as string. Subclasses are
        expected to override this method with their own version string generators, which then might
        include git commit hashes, git commit date and time, bzr revision, etc..

        Returns:
            str:        formatted version string
        """

        return self.spkg.conf.get("source", "version")

    def execute(self) -> bool:
        """
        This method provides a generic way of preparing a package's sources. This will invoke the
        :py:meth`Source.get()` method or the :py:meth`Source.update()` method and the
        :py:meth`Source.export()` method (as overridden by the subclass, respectively).

        If sources can be downloaded / copied into place successfully, an update for them will not
        be attempted. Otherwise (sources are already present within the package directory), an
        update will be attempted before exporting.

        Returns:
            bool:       success status of source getting or updating
        """

        get_success = self.get()
        if get_success:
            return self.export()

        update_success = self.update()
        if update_success:
            return self.export()

        return False

    def refresh(self) -> bool:
        """
        This method provides a generic way of refreshing a package's sources. This will invoke the
        generic :py:meth:`Source.clean()` method and the :py:meth`Source.get()` method (as
        overridden by the subclass).

        Returns:
            bool:       success status of source getting
        """

        self.clean()
        success = self.get()
        return success
