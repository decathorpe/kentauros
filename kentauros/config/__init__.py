"""
kentauros.config module
"""

__all__ = ["envVar", "rcFile", "xdgConfig"]


import os


HOME_PATH = os.environ.get("HOME")

KTR_CONF_PATH = os.environ.get("KTR_CONF_DIR")
KTR_SRC_PATH = os.environ.get("KTR_SRC_DIR")

if HOME_PATH is None:
    HOME_PATH = "/tmp/ktr"

if KTR_CONF_PATH is None:
    KTR_CONF_PATH = "./"

if KTR_SRC_PATH is None:
    KTR_SRC_PATH = "./"

