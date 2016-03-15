"""
This module contains the 'run' and 'run_config' main functions that are
called when the package is executed by the setuptools-installed 'ktr' or
'ktr-config' scripts.
"""

from kentauros.run.ktr import run
from kentauros.run.ktr_config import run_config


__all__ = ["run", "run_config"]

