#!/usr/bin/env python3

from setuptools import setup

setup(
    name="kentauros",
    version="0.0.3",
    author="Fabio Valentini",
    author_email="decathorpe@gmail.com",
    description="build system for building RPM package from upstream sources",
    license="GPLv2",
    keywords="development packaging",
    url="http://github.com/decathorpe/kentauros",
    packages=['kentauros'],
    scripts=['ktr'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5']
)

