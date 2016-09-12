"""
This subpackage serves the purpose of handling RPM spec files.
"""


import os

from kentauros.sources.src_abstract import Source

from kentauros.pkgformat.rpm.spec_common import RPMSpecError
from kentauros.pkgformat.rpm.spec_preamble_out import SPEC_PREAMBLE_DICT
from kentauros.pkgformat.rpm.spec_version_out import SPEC_VERSION_DICT


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

    def get_version_from_file(self):
        """
        This method reads and parses the RPM spec file for its "Version" tag.

        Returns:
            str: version string found on the line containing the "Version:" tag
        """

        with open(self.path, "r") as spec_file:
            for line in spec_file:
                if line[0:8] == "Version:":
                    return line.replace("Version:", "").lstrip(" \t").rstrip("\n")

            raise RPMSpecError("No Version tag was found in the file.")

    def get_release_from_file(self):
        """
        This method reads and parses the RPM spec file for its "Release" tag.

        Returns:
            str: release string found on the line containing the "Version:" tag
        """

        with open(self.path, "r") as spec_file:
            for line in spec_file:
                if line[0:8] == "Release:":
                    return line.replace("Release:", "").lstrip(" \t").rstrip("\n")

            raise RPMSpecError("No Version tag was found in the file.")

    def get_preamble_string(self):
        """
        This method returns the appropriate spec preamble string, depending on the type of Source
        that has been set.

        Returns:
            str:    preamble string containing necessary definitions
        """

        return SPEC_PREAMBLE_DICT[self.source.stype](self.source)

    def get_version_string(self):
        """
        This method returns the appropriate spec line containing the "Version" tag, depending on the
        type of Source that has been set.

        Returns:
            str:    preamble string containing necessary definitions
        """

        return SPEC_VERSION_DICT[self.source.stype](self.source)
