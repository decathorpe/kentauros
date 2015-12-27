#!/usr/bin/env python3

from setuptools import setup

setup(
    name = "kentauros",
    version = "0.0.2",
    author = "Fabio Valentini",
    author_email = "decathorpe (at) gmail (dot) com",
    description = "small build system, written in python",
    license = "GPLv2",
    keywords = "development packaging",
    url = "http://github.com/decathorpe/kentauros",
    packages = ['kentauros'],
    scripts = ['ktr'],
)
