"""
This subpackage contains the quasi-abstract :py:class:`Builder` class and its
:py:class:`MockBuilder` subclass, which are used to hold information about the configured local
builder for binary packages. This includes only :py:class:`MockBuilder` right now, but should be
extensible for other builders without need for architectural changes. Additionally, this file
contains a dictionary which maps :py:class:`BuilderType` enums to their respective class
constructors.
"""


from kentauros.definitions import BuilderType

from kentauros.modules.builder.abstract import Builder
from kentauros.modules.builder.mock import MockBuilder


def get_builder(btype: BuilderType, package) -> Builder:
    """
    This function constructs a `Builder` from a `BuilderType` enum member and a package.
    """

    builder_dict = dict()

    builder_dict[BuilderType.MOCK] = MockBuilder

    return builder_dict[btype](package)
