"""
This sub-module serves provides shared code for this subpackage. This includes:

 * :py:class:`RPMSpecError`: custom exception that is raised when errors occur during the parsing
   of .spec files
 * :py:func:`format_tag_line`: simple function generating prettified spec tag lines

"""


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


def format_tag_line(tag: str, value: str) -> str:
    """
    This function takes a tag and value as arguments and returns a nicely formatted tag line,
    aligning values after column 16 (second / fourth tab).

    Arguments:
        str tag:    tag of tag line
        str value:  tag value

    Returns:
        str:        pretty tag line
    """

    return tag + ":" + (16 - len(tag) - 1) * " " + value + "\n"
