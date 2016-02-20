#!/usr/bin/env python3

from setuptools import setup

from kentauros import KTR_SYSTEM_DATADIR


setup(
    name="kentauros",
    version="0.0.4",
    author="Fabio Valentini",
    author_email="decathorpe@gmail.com",
    description="build system for building RPM package from upstream sources",
    license="GPLv2",
    keywords="development packaging",
    url="http://github.com/decathorpe/kentauros",
    packages=['kentauros'],
    scripts=['ktr'],
    data_files=[(KTR_SYSTEM_DATADIR, ['data/default.conf']),
                (KTR_SYSTEM_DATADIR, ['data/package.conf'])],
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

