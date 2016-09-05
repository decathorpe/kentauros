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
    description="build system for building RPM package from upstream sources",
    license="GPLv2",
    keywords="development packaging",
    url="http://github.com/decathorpe/kentauros",
    packages=find_packages(),
    install_requires=["dataset", "python-dateutil"],
    entry_points={'console_scripts': [
        'ktr = kentauros.run.ktr:run',
        'ktr-config = kentauros.run.ktr_config:run_config',
        'ktr-create = kentauros.run.ktr_create:run_create']},
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
