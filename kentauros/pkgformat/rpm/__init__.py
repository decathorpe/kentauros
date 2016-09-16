"""
This subpackage serves the purpose of handling RPM spec files.
"""


import os
import subprocess

from kentauros.instance import Kentauros

from kentauros.sources.src_abstract import Source

from kentauros.pkgformat.rpm.spec_common import RPMSpecError, format_tagline
from kentauros.pkgformat.rpm.spec_preamble_out import SPEC_PREAMBLE_DICT
from kentauros.pkgformat.rpm.spec_version_out import SPEC_VERSION_DICT


LOGPREFIX = "ktr/pkgformat/rpm"
"""This string specifies the prefix for log and error messages printed to stdout or stderr from
inside this subpackage.
"""


class RPMSpec:
    """
    This class serves as the go-to toolbelt for handling everything concerning RPM spec files
    from within kentauros.

    Attributes:
        str path:       path pointing to the associated RPM spec file
        Source source:  package sources that are needed to generate some information
    """

    def __init__(self, path: str, source: Source):
        assert isinstance(path, str)
        assert isinstance(source, Source)

        if not os.path.exists(path):
            raise FileNotFoundError()

        self.path = path
        self.source = source
        self.contents = self._get_contents()

        self.saved_preamble = None

    def _get_contents(self) -> str:
        """
        This method reads the contents of the file at `self.path` and returns them.

        Returns:
            str:    .spec file contents
        """

        with open(self.path, "r") as file:
            contents = file.read()
            return contents

    def _set_contents(self):
        """
        This method write the in-memory contents to the file at `self.path`.
        """

        with open(self.path, "w") as file:
            file.write(self.contents)

    def _get_lines(self) -> list:
        """
        This method splits the contents of the .spec file into lines and returns a list of them.

        Returns:
            list:   list of lines
        """

        return self.contents.split("\n")

    def read_version(self) -> str:
        """
        This method reads and parses the RPM spec file's contents for its "Version" tag.

        Returns:
            str:    version string found on the line containing the "Version:" tag
        """

        for line in self._get_lines():
            if line[0:8] == "Version:":
                return line.replace("Version:", "").lstrip(" \t").rstrip()

        raise RPMSpecError("No Version tag was found in the file.")

    def read_release(self) -> str:
        """
        This method reads and parses the RPM spec file's contents for its "Release" tag.

        Returns:
            str:    release string found on the line containing the "Version:" tag
        """

        for line in self._get_lines():
            if line[0:8] == "Release:":
                return line.replace("Release:", "").lstrip(" \t").rstrip()

        raise RPMSpecError("No Version tag was found in the file.")

    def write_version(self):
        """
        This method writes the updated version to the rpm spec file.
        """

        contents_new = str()

        for line in self._get_lines():
            if line[0:8] != "Version:":
                assert isinstance(line, str)
                contents_new += (line + "\n")
            else:
                contents_new += format_tagline("Version", self.build_version_string())

        self.contents = contents_new
        self._set_contents()

    def build_preamble_string(self) -> str:
        """
        This method returns the appropriate spec preamble string, depending on the type of Source
        that has been set.

        Returns:
            str:    preamble string containing necessary definitions
        """

        return SPEC_PREAMBLE_DICT[self.source.stype](self.source)

    def build_version_string(self) -> str:
        """
        This method returns the appropriate spec line containing the "Version" tag, depending on the
        type of Source that has been set.

        Returns:
            str:    preamble string containing necessary definitions
        """

        return SPEC_VERSION_DICT[self.source.stype](self.source)

    def prepend_preamble(self):
        """
        This method prepends the necessary preamble to the contents here and on disk.
        """

        self.saved_preamble = self.build_preamble_string()
        self.contents = self.saved_preamble + self.contents
        self._set_contents()

    def unprepend_preamble(self):
        """
        This method removes the prepended preamble from the spec file's contents here and on disk.
        """

        assert self.saved_preamble is not None
        self.contents = self.contents.replace(self.saved_preamble, "")
        self._set_contents()

    def do_release_reset(self):
        """
        This method resets the release number to 0suffix.
        """

        old_rel = self.read_release()
        new_rel = str(0) + old_rel[1:]

        contents_new = str()

        for line in self._get_lines():
            if line[0:8] != "Release:":
                assert isinstance(line, str)
                contents_new += (line + "\n")
            else:
                contents_new += format_tagline("Release", new_rel)

        self.contents = contents_new
        self._set_contents()

    def do_release_bump(self, comment: str=None):
        """
        This method calls `rpmdev-bumpspec` with the specified arguments to bump the release number
        and create a changelog entry with a given comment.

        Arguments:
            str comment:    comment to be added to the changelog entry
        """

        ktr = Kentauros(LOGPREFIX)

        if comment is None:
            comment = "Automatic build by kentauros."

        # construct rpmdev-bumpspec command
        cmd = ["rpmdev-bumpspec"]

        # add --verbose or --quiet depending on settings
        if (ktr.verby == 0) or ktr.debug:
            cmd.append("--verbose")

        cmd.append(self.path)
        cmd.append('--comment="' + comment + '"')

        ktr.log_command(cmd)
        subprocess.call(cmd)

        # TODO: error handling

        self.contents = self._get_contents()
