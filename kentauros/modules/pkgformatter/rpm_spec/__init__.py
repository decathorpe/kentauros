import os

from kentauros.definitions import SourceType

from kentauros.modules.sources.abstract import Source

from kentauros.modules.sources.bzr import BzrSource
from kentauros.modules.sources.git import GitSource
from kentauros.modules.sources.url import UrlSource
from kentauros.modules.sources.local import LocalSource


class RPMSpecError(Exception):
    """
    This custom exception will be raised when errors occur during parsing of an RPM spec file.

    Arguments:
        str value:  informational string accompanying the exception
    """

    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


def format_tagline(tag: str, value: str) -> str:
    """
    This function takes a tag and value as arguments and returns a nicely formatted tagline,
    aligning values after column 16 (second / fourth tab).

    Arguments:
        str tag:    tag of tagline
        str value:  tag value

    Returns:
        str:        pretty tagline
    """

    return tag + ":" + (16 - len(tag) - 1) * " " + value + "\n"


def spec_preamble_bzr(source: BzrSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from *bzr* repositories.
    This includes a definition of "rev" just now.

    Arguments:
        BzrSource source:   source repository the revision will be determined from

    Returns:
        str:                string containing the ``%defines rev $REV`` line
    """

    assert isinstance(source, BzrSource)
    rev_define = "%define rev " + source.rev() + "\n"
    return rev_define + "\n"


def spec_preamble_git(source: GitSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from *git* repositories. This
    includes a definition of "commit" and "date" just now. The value of "cpmmit" here are the first
    8 characters of the corresponding git commit hash.

    Arguments:
        GitSource source:   source repository the commit hash and date will be determined from

    Returns:
        str:                string with the "%defines commit COMMIT" and "%defines date $DATE" lines
    """

    assert isinstance(source, GitSource)
    date_define = "%define date " + source.date() + "\n"
    commit_define = "%define commit " + source.commit()[0:8] + "\n"
    return date_define + commit_define + "\n"


def spec_preamble_url(source: UrlSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from tarballs specified by
    *url*.

    Arguments:
        UrlSource source:   source the ``%defines`` will be determined from

    Returns:
        str:                empty string
    """

    assert isinstance(source, UrlSource)
    return ""


def spec_preamble_local(source: LocalSource) -> str:
    """
    This function returns the "%defines" necessary for packages built from tarballs specified by a
    *local path*.

    Arguments:
        LocalSource source:     source the ``%defines`` will be determined from

    Returns:
        str:                    empty string
    """

    assert isinstance(source, LocalSource)
    return ""


SPEC_PREAMBLE_DICT = dict()
"""This dictionary maps `SourceType` enum members to their respectiv RPM spec preamble generator
functions.
"""

SPEC_PREAMBLE_DICT[SourceType.BZR] = spec_preamble_bzr
SPEC_PREAMBLE_DICT[SourceType.GIT] = spec_preamble_git
SPEC_PREAMBLE_DICT[SourceType.LOCAL] = spec_preamble_local
SPEC_PREAMBLE_DICT[SourceType.URL] = spec_preamble_url


def spec_source_bzr(source: BzrSource) -> str:
    """
    This function returns the Source tag for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a Source tag will be generated for

    Returns:
        str:                Source tag with comments
    """

    assert isinstance(source, BzrSource)

    src_str = ("# The tarball is generated from a checkout of the specified branch and\n" +
               "# by executing 'bzr export' and has the usual format\n" +
               "# ('%{name}-%{version}.tar.gz'), where %{version} contains the upstream\n" +
               "# version number with a '+bzr%{rev}' suffix specifying the bzr revision.\n" +
               format_tagline("Source0", "%{name}-%{version}.tar.gz"))

    return src_str


def spec_source_git(source: GitSource) -> str:
    """
    This function returns the Source string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a Source tag will be generated for

    Returns:
        str:                Source tag with comments
    """

    assert isinstance(source, GitSource)

    src_str = ("# The tarball is generated from a clone of the specified branch and\n" +
               "# by executing 'git archive' and has the usual format\n" +
               "# ('%{name}-%{version}.tar.gz'), where %{version} contains the upstream\n" +
               "# version number with a '+git%{commit}.%{date}' suffix specifying the git\n"
               "# commit hash (8 characters) and the commit date and time (UTC).\n" +
               format_tagline("Source0", "%{name}-%{version}.tar.gz"))

    return src_str


def spec_source_local(source: LocalSource) -> str:
    """
    This function returns the Source string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a Source tag will be generated for

    Returns:
        str:                    Source tag in the format `Source0: $VERSION`
    """

    assert isinstance(source, LocalSource)

    src_str = format_tagline("Source0", os.path.basename(source.spkg.conf.get("local", "orig")))
    return src_str


def spec_source_url(source: UrlSource) -> str:
    """
    This function returns the Source string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a Source tag will be generated for

    Returns:
        str:                Source tag in the format `Source0: $URL`
    """

    assert isinstance(source, UrlSource)

    src_str = format_tagline("Source0", source.spkg.conf.get("url", "orig"))
    return src_str


SPEC_SOURCE_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec Source tag string
generator functions.
"""

SPEC_SOURCE_DICT[SourceType.BZR] = spec_source_bzr
SPEC_SOURCE_DICT[SourceType.GIT] = spec_source_git
SPEC_SOURCE_DICT[SourceType.LOCAL] = spec_source_local
SPEC_SOURCE_DICT[SourceType.URL] = spec_source_url


def spec_version_bzr(source: BzrSource) -> str:
    """
    This function returns the version string for packages built from *bzr* repositories.

    Arguments:
        BzrSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format ``$VERSION+rev%{rev}``
    """

    assert isinstance(source, BzrSource)
    ver_str = source.spkg.get_version() + "+rev%{rev}"
    return ver_str


def spec_version_git(source: GitSource) -> str:
    """
    This function returns the version string for packages built from *git* repositories.

    Arguments:
        GitSource source:   source repository a version string will be generated for

    Returns:
        str:                version string in the format ``$VERSION+git%{date}.%{commit}``
    """

    assert isinstance(source, GitSource)
    ver_str = source.spkg.get_version() + "+git%{date}.%{commit}"
    return ver_str


def spec_version_local(source: LocalSource) -> str:
    """
    This function returns the version string for packages built from tarballs specified by a *local
    path*.

    Arguments:
        LocalSource source:     source a version string will be generated for

    Returns:
        str:                    version string in the format ``$VERSION``
    """

    assert isinstance(source, LocalSource)
    ver_str = source.spkg.get_version()
    return ver_str


def spec_version_url(source: UrlSource) -> str:
    """
    This function returns the version string for packages built from tarballs specified by *url*.

    Arguments:
        UrlSource source:   source a version string will be generated for

    Returns:
        str:                version string in the format ``$VERSION``
    """

    assert isinstance(source, UrlSource)
    ver_str = source.spkg.get_version()
    return ver_str


SPEC_VERSION_DICT = dict()
""" This dictionary maps `SourceType` enum members to their respective RPM spec version string
generator functions.
"""

SPEC_VERSION_DICT[SourceType.BZR] = spec_version_bzr
SPEC_VERSION_DICT[SourceType.GIT] = spec_version_git
SPEC_VERSION_DICT[SourceType.LOCAL] = spec_version_local
SPEC_VERSION_DICT[SourceType.URL] = spec_version_url


class RpmSpec:
    """
    This class serves as the go-to toolbelt for handling everything concerning RPM spec files
    from within kentauros.

    The typical usage has 3 stages:

    * reading from file (path that is passed at initialisation)
    * manipulating .spec file contents
    * writing to different file path

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

        with open(path, "r") as file:
            self.contents = file.read()

    def get_lines(self) -> list:
        """
        This method splits the contents of the .spec file into lines and returns a list of them.

        Returns:
            list:   list of lines
        """

        return self.contents.split("\n")

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

        raise RPMSpecError("No Version tag was found in the file.")

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
                contents_new += format_tagline("Version", self.build_version_string())

        self.contents = contents_new

    def set_source(self):
        """
        This method writes the updated source tag to the rpm spec file.
        """

        contents_new = str()

        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] != "Source0:":
                contents_new += (line + "\n")
            else:
                contents_new += SPEC_SOURCE_DICT[self.source.stype](self.source)

        self.contents = contents_new

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

    def export_to_file(self, path: str):
        """
        This method exports the .spec file's (modified in memory) contents to another file,
        specified by the `path` argument.

        Arguments:
            str path:   path to write the modified .spec contents to
        """

        file_contents = str()
        file_contents += self.build_preamble_string()
        file_contents += self.contents

        if path == self.path:
            raise RPMSpecError("Overriding the original .spec file is not supported.")

        with open(path, "w") as file:
            file.write(file_contents)

    def do_release_reset(self):
        """
        This method resets the release number to 0suffix.
        """

        old_rel = self.get_release()
        new_rel = str(0) + old_rel[1:]

        contents_new = str()

        for line in self.get_lines():
            if line[0:8] != "Release:":
                assert isinstance(line, str)
                contents_new += (line + "\n")
            else:
                contents_new += format_tagline("Release", new_rel)

        self.contents = contents_new
