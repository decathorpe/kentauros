#!/usr/bin/env python3

from setuptools import setup, find_packages

from kentauros.definitions import KTR_SYSTEM_DATADIR, KTR_VERSION


setup(
    name="kentauros",
    version=KTR_VERSION,
    author="Fabio Valentini",
    author_email="decathorpe@gmail.com",
    description="build system for building RPM package from upstream sources",
    license="GPLv2",
    keywords="development packaging",
    url="http://github.com/decathorpe/kentauros",
    packages=find_packages(),
    entry_points={'console_scripts': ['ktr = kentauros.run:run',],},
    data_files=[(KTR_SYSTEM_DATADIR, ['data/default.conf']),
                (KTR_SYSTEM_DATADIR, ['data/template.conf']),
                (KTR_SYSTEM_DATADIR, ['data/template.spec'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5']
)

