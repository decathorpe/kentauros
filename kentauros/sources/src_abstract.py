"""
This module contains the template / dummy :py:class:`Source` class, which
is then inherited by actual sources.
"""

# TODO: remove Source.conf attribute
# TODO: remove Source.name attribute

import abc
import os
import shutil

from kentauros.instance import Kentauros, log


LOGPREFIX1 = "ktr/sources: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class Source(metaclass=abc.ABCMeta):
    """
    This class serves as an abstract base class for source package
    uploaders. They are expected to override this class's unimplemented methods.
    It also provides common infrastructure for all code sources in the form of
    generalised implementations of get, refresh and formatver methods.

    Attributes:
        str name:           package name
        str sdir:           source directory of the package this source belongs to
        str dest:           destination path when downloading / copying sources
        str orig:           origin of the source, as specified in the package configuration file
        bool keep:          determines wheather sources are kept between actions
        ConfigParser conf:  package configuration object
        Package package:    mother package
        SourceType type:    type of source
    """

    def __init__(self, package):
        self.conf = package.conf

        self.name = self.conf['package']['name']

        self.sdir = os.path.join(Kentauros().conf.get_datadir(), self.name)
        self.dest = None
        self.orig = None
        self.keep = False

        self.spkg = package
        self.stype = None

    @abc.abstractmethod
    def export(self):
        """
        This dummy method will be overridden by subclasses. It is expected that
        an appropriately named tarball is present within the package's source
        directory after this method has been executed.
        """

    @abc.abstractmethod
    def get(self):
        """
        This dummy method will be overridden by subclasses. It is expected that
        an appropriately named source file or directory is present within the
        package's source directory after this method has been executed.
        """

    @abc.abstractmethod
    def update(self):
        """
        This dummy method will be overridden by subclasses. It is expected that
        the source repository present within the package's source directory is
        up-to-date with upstream sources after this method has been executed,
        except when package configuration specifies something else explicitely.
        """

    def clean(self) -> bool:
        """
        This method cleans up all of a package's sources (removes the source
        directory completely).

        Returns:
            bool:   `True` if successful, `False` if directory doesn't exist
        """

        if not os.path.exists(self.sdir):
            log(LOGPREFIX1 + "Nothing here to be cleaned.", 0)
            return False
        else:
            # try to be careful with "rm -r"
            assert os.path.isabs(self.sdir)
            assert Kentauros().conf.get_datadir() in self.sdir
            shutil.rmtree(self.sdir)
            return True

    def formatver(self) -> str:
        """
        This method provides a generic way of getting a package's version as
        string. Subclasses are expected to override this method with their own
        version string generators, which then might include git commit hashes,
        git commit date and time, bzr revision, etc..

        Returns:
            str:        formatted version string
        """

        return self.spkg.conf.get("source", "version")

    def prepare(self) -> bool:
        """
        This method provides a generic way of preparing a package's sources.
        This will invoke the :py:meth`Source.get()` method or the
        :py:meth`Source.update()` method and the :py:meth`Source.export()`
        method (as overridden by the subclass, respectively).

        If sources can be downloaded / copied into place successfully, an
        update for them will not be attempted. Otherwise (sources are already
        present within the package directory), an update will be attempted
        before exporting.

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
        This method provides a generic way of refreshing a package's sources.
        This will invoke the generic :py:meth:`Source.clean()` method and the
        :py:meth`Source.get()` method (as overridden by the subclass).

        Returns:
            bool:       success status of source getting
        """

        self.clean()
        success = self.get()
        return success
