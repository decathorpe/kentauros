"""
This subpackage serves the purpose of handling RPM spec files.
"""

import configparser as cp
import os
import subprocess

from ....context import KtrContext
from ....definitions import SourceType
from ....logcollector import LogCollector
from ....package import KtrPackage
from ....result import KtrResult

from .spec_common import RPMSpecError, format_tag_line
from .spec_preamble_out import SPEC_PREAMBLE_DICT
from .spec_source_out import SPEC_SOURCE_DICT
from .spec_version_out import SPEC_VERSION_DICT


def parse_release(release: str) -> (str, str):
    """
    This function splits the Release string into the leading numeric part and the trailing
    alphanumeric part.

    Arguments:
        str release:    Release string

    Returns:
        str, str:       numeric part, trailing part
    """

    if "%{dist}" in release:
        parts = release.split("%{dist}")
        part1 = parts[0]
        part2 = "%{dist}" + parts[1]
    else:
        part1 = release
        part2 = ""

    num_string = str()

    for char in part1:
        if char.isnumeric():
            num_string += char
        else:
            break

    abc_string = part1.lstrip("0123456789")

    return num_string, abc_string + part2


class RPMSpec:
    """
    This class serves as the go-to swiss army knife for handling everything concerning RPM spec
    files from within kentauros.

    The typical usage has 3 stages:

    * reading from file (path that is passed at initialisation)
    * manipulating .spec file contents
    * writing to different file path

    Attributes:
        str path:       path pointing to the associated RPM spec file
        Source source:  package sources that are needed to generate some information
    """

    def __init__(self, path: str, package: KtrPackage, context: KtrContext):
        assert isinstance(path, str)
        assert isinstance(package, KtrPackage)
        assert isinstance(context, KtrContext)

        if not os.path.exists(path):
            raise FileNotFoundError()

        self.path = path
        self.package = package
        self.context = context

        try:
            self.stype = SourceType[self.package.conf.get("modules", "source").upper()]
        except cp.NoSectionError:
            self.stype = None
        except cp.NoOptionError:
            self.stype = None
        except KeyError:
            self.stype = None

        with open(path, "r") as file:
            self.contents = file.read()

    def get_lines(self) -> list:
        """
        This method splits the contents of the .spec file into lines and returns a list of them. It
        also removes the trailing newline at the end of files so they don't multiply like rabbits.

        Returns:
            list:   list of lines
        """

        return self.contents.split("\n")[:-1]

    def get_version(self) -> str:
        """
        This method reads and parses the RPM spec file's contents for its "Version" tag.

        Returns:
            str:    version string found on the line containing the "Version:" tag
        """

        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] == "Version:":
                return line.replace("Version:", "").lstrip(" \t").rstrip()

        raise RPMSpecError("No Version tag was found in the file.")

    def get_release(self) -> str:
        """
        This method reads and parses the RPM spec file's contents for its "Release" tag.

        Returns:
            str:    release string found on the line containing the "Version:" tag
        """

        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] == "Release:":
                return line.replace("Release:", "").lstrip(" \t").rstrip()

        raise RPMSpecError("No Release tag was found in the file.")

    def set_version(self):
        """
        This method writes the updated version to the rpm spec file.
        """

        contents_new = str()

        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] != "Version:":
                contents_new += (line + "\n")
            else:
                contents_new += format_tag_line("Version", self.build_version_string())

        self.contents = contents_new

    def set_source(self):
        """
        This method writes the updated source tag to the rpm spec file.
        """

        contents_new = str()

        for line in self.get_lines():
            assert isinstance(line, str)
            if (line[0:8] != "Source0:") and (line[0:7] != "Source:"):
                contents_new += (line + "\n")
            else:
                if self.stype is not None:
                    contents_new += SPEC_SOURCE_DICT[self.stype](self.package)

        self.contents = contents_new

    def build_preamble_string(self) -> KtrResult:
        """
        This method returns the appropriate spec preamble string, depending on the type of Source
        that has been set.

        Returns:
            str:    preamble string containing necessary definitions
        """

        return SPEC_PREAMBLE_DICT[self.stype](self.package, self.context)

    def build_version_string(self) -> str:
        """
        This method returns the appropriate spec line containing the "Version" tag, depending on the
        type of Source that has been set.

        Returns:
            str:    preamble string containing necessary definitions
        """

        return SPEC_VERSION_DICT[self.stype](self.package, self.context)

    def export_to_file(self, path: str):
        """
        This method exports the .spec file's (modified in memory) contents to another file,
        specified by the `path` argument.

        Arguments:
            str path:   path to write the modified .spec contents to
        """

        assert isinstance(path, str)

        if path == self.path:
            os.remove(path)

        res = self.build_preamble_string()
        if not res.success:
            raise NotImplementedError("The RPM .spec handler can't work successfully.")
        preamble = res.value

        with open(path, "w") as file:
            file.write(preamble)
            file.write(self.contents)

    def write_contents_to_file(self, path: str):
        """
        This method writes the .spec file's (modified in memory) contents to another file,
        specified by the `path` argument (BUT without prepending the preamble).

        Arguments:
            str path:   path to write the modified .spec contents to
        """

        assert isinstance(path, str)

        if path == self.path:
            os.remove(path)

        with open(path, "w") as file:
            file.write(self.contents)

    def do_release_reset(self):
        """
        This method resets the release number to 0suffix.
        """

        new_rel = str(0) + parse_release(self.get_release())[1]

        contents_new = str()

        for line in self.get_lines():
            if line[0:8] != "Release:":
                assert isinstance(line, str)
                contents_new += (line + "\n")
            else:
                contents_new += format_tag_line("Release", new_rel)

        self.contents = contents_new


def do_release_bump(path: str, context: KtrContext, comment: str = None) -> KtrResult:
    """
    This function calls `rpmdev-bumpspec` with the specified arguments to bump the release number
    and create a changelog entry with a given comment.

    Arguments:
        str comment:    comment to be added to the changelog entry
    """

    logger = LogCollector("RPM .spec Handler")
    ret = KtrResult(messages=logger)

    if not os.path.exists(path):
        raise FileNotFoundError()

    if comment is None:
        comment = "Automatic build by kentauros."

    # construct rpmdev-bumpspec command
    cmd = ["rpmdev-bumpspec"]

    # add --verbose or --quiet depending on settings
    if context.debug:
        cmd.append("--verbose")

    cmd.append(path)
    cmd.append('--comment=' + comment)

    logger.cmd(cmd)
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    success = (res.returncode == 0)

    return ret.submit(success)
