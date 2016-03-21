"""
kentauros.init.env file
"""

import os


def get_env_home():
    if "HOME" in os.environ:
        return os.environ.get("HOME")
    else:
        return os.path.abspath("./")


def get_env_debug():
    if "KTR_DEBUG" in os.environ:
        return bool(os.environ.get("KTR_DEBUG"))
    else:
        return False


def get_env_verby():
    if "KTR_VERBOSITY" in os.environ:
        return int(os.environ.get("KTR_VERBOSITY"))
    else:
        return 2

