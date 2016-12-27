"""
This sub-module only includes a custom Exception that is raised if unrecoverable errors occur during
the execution of a Source module code.
"""


class SourceError(Exception):
    """
    This custom exception will be raised when unrecoverable errors occur during execution of a
    Source module.

    Arguments:
        str value:  informational string accompanying the exception
    """

    def __init__(self, value=""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)
