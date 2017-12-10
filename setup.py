#!/usr/bin/env python3

"""
setuptools install script for kentauros
"""

from setuptools import setup, find_packages

from kentauros.definitions import KTR_SYSTEM_DATADIR, KTR_VERSION


setup(
    name="kentauros",
    version=KTR_VERSION,
    author="Fabio Valentini",
    author_email="decathorpe@gmail.com",
    description="Modular, automatic and configurable package build system",
    license="GPLv2",
    keywords="development packaging",
    url="http://github.com/decathorpe/kentauros",
    packages=find_packages(exclude=['data', 'docs', 'examples', 'meta', 'scripts']),
    install_requires=["argcomplete", "tinydb", "GitPython"],
    scripts=['scripts/ktr'],
    data_files=[(KTR_SYSTEM_DATADIR, ['data/default.conf']),
                (KTR_SYSTEM_DATADIR, ['data/template.conf'])],
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
