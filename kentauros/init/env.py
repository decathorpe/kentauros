"""
This module contains simple functions for parsing environment variables needed for basic functions
and determining debug and verbosity level.
"""


import os


def get_env_home() -> str:
    """
    This function tries to get the home directory of the user running ktr. If the `HOME` variable is
    not set, the current directory is used.

    Returns:
        str:    environment variable for `HOME` or the current directory
    """

    if "HOME" in os.environ:
        return os.environ.get("HOME")
    else:
        return os.path.abspath("./")


def get_env_debug() -> bool:
    """
    This function returns *True* if the "*KTR_DEBUG*" environment variable was set to anything
    parse-able to *True* by python. If not (or the variable has not been set), it returns *False*.

    Returns:
        bool:   debug *on* or *off*
    """

    if "KTR_DEBUG" in os.environ:
        return bool(os.environ.get("KTR_DEBUG"))
    else:
        return False


def get_env_verby() -> int:
    """
    This function returns the parsed value of the `KTR_VERBOSITY` environment variable (anything
    parse-able to an `int` by python. If it has not been set, it will return *2* (the lowest
    verbosity level).

    Returns:
        int:    verbosity level
    """

    if "KTR_VERBOSITY" in os.environ:
        return int(os.environ.get("KTR_VERBOSITY"))
    else:
        return 2
