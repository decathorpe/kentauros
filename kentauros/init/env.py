"""
kentauros.init.env file
"""

import os


def get_env_home():
    return os.environ.get("HOME")

def get_env_debug():
    if os.getenv("KTR_DEBUG") is None:
        return False
    else:
        return True

def get_env_verby():
    if os.environ.get("KTR_VERBOSITY") is None:
        return 2
    else:
        return int(os.environ.get("KTR_VERBOSITY"))

