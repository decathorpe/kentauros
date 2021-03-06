#!/usr/bin/env python3

"""
setuptools install script for kentauros
"""

import unittest
from setuptools import setup, find_packages

from kentauros import KTR_VERSION


def test_suite():
    loader = unittest.TestLoader()
    suite = loader.discover("kentauros", pattern="*_test.py")
    return suite


setup(
    name="kentauros",
    version=KTR_VERSION,

    author="Fabio Valentini",
    author_email="decathorpe@gmail.com",

    description="Modular, automatic and configurable package build system",
    url="http://github.com/decathorpe/kentauros",
    license="GPLv2",

    keywords="development packaging",

    packages=find_packages(exclude=['data', 'docs', 'examples', 'meta', 'scripts']),
    install_requires=["argcomplete", "tinydb", "GitPython"],

    test_suite="setup.test_suite",

    scripts=['scripts/ktr'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6']
)
