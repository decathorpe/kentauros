#!/usr/bin/python3 -Wa

# PYTHON_ARGCOMPLETE_OK

import os
import sys

sys.path.insert(0, os.getcwd())

# pylint: disable=wrong-import-position

from kentauros import KtrCLIRunner

sys.exit(KtrCLIRunner().run())
