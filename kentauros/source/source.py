"""
# TODO: napoleon module docstring
kentauros.source.common
contains Source class definition
"""


import os
import shutil

from kentauros.instance import Kentauros, log


LOGPREFIX1 = "ktr/source: "
"""This string specifies the prefix for log and error messages printed to
stdout or stderr from inside this subpackage.
"""


class Source():
    """
    # TODO: napoleon class docstring
    kentauros.source.common.Source
    class that contains information about upstream source code and
    methods that depend on it.
    - name: name that upstream source should get (filename or VCS repodir name)
    - sdir: directory that contains all source files of the package
    - dest: destination where upstream source is put (override in subclasses)
    - orig: origin of upstream sources (URL to file, git repo, etc.)
    - type: determines type of upstream source
    - keep: determines if sources are kept between builds
    """

    def __init__(self, package):
        self.package = package
        self.conf = package.conf
        self.name = self.conf['package']['name']
        self.sdir = os.path.join(Kentauros().conf.datadir, self.name)
        self.type = None


    def clean(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.clean():
        default method of cleaning up sources in datadir/pkgname
        - returns False if sdir does not exist.
        - returns True after successful cleaning.
        """

        if not os.path.exists(self.sdir):
            log(LOGPREFIX1 + "Nothing here to be cleaned.", 0)
            return False
        else:
            # try to be careful with "rm -r"
            assert os.path.isabs(self.sdir)
            assert Kentauros().conf.datadir in self.sdir
            shutil.rmtree(self.sdir)
            return True


    def export(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.export():
        default method for source exporting; override as neccessary
        - return True when successful
        - return False when not
        """

        log(LOGPREFIX1 + "Dummy method for exporting " + \
            self.name + " sources invoked. No action will be executed.")
        return False


    def formatver(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.formatver():
        default method for getting source version string; override as neccessary
        by default this is the string found in package configuration
        override as neccesary (e.g. bzr rev, git date/commit hash, etc.)
        """

        return self.package.conf.get("source", "version")


    def get(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.get():
        default method for downloading/copying sources; override as neccessary
        - return True when successful
        - return False when not
        """

        log(LOGPREFIX1 + "Dummy method for getting " + \
            self.name + " sources invoked. No action will be executed.")
        return False


    def refresh(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.refresh():
        default method for refreshing sources (clean and get)
        returns success value from .get()
        """

        self.clean()
        success = self.get()
        return success


    def update(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.update():
        default method for updating sources; override as neccessary
        - return True when update was successful and available
        - return False when either unsuccessful or no update available
        """

        log(LOGPREFIX1 + "Dummy method for updating " + \
            self.name + " sources invoked. No action will be executed.")
        return False


    def prepare(self):
        """
        # TODO: napoleon method docstring
        kentauros.source.common.Source.prepare():
        default method for preparing sources (get/update, export)
        - return True when all steps were successful
        - return False when something fails (either get/update or export)
        """

        get_success = self.get()
        if get_success:
            return self.export()

        update_success = self.update()
        if update_success:
            return self.export()

        return False
