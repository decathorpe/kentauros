#!/usr/bin/python3 -Wa

# PYTHON_ARGCOMPLETE_OK

import os
import sys

sys.path.insert(0, os.getcwd())

from kentauros.cli import KtrCLIRunner

sys.exit(KtrCLIRunner().run())
