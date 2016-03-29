"""
This subpackage contains the quasi-abstract :py:class:`Builder` class and its
:py:class:`MockBuilder` subclass, which are used to hold information about the
configured local builder for binary packages. This includes only
:py:class:`MockBuilder` rightnow, but should be extensible for other builders
without need for architectural changes. Additionally, this file contains a
dictioary which maps :py:class:`BuilderType` enums to their respective class
constructors.
"""


from kentauros.definitions import BuilderType

from kentauros.build.builder import Builder
from kentauros.build.mock import MockBuilder


__all__ = ["builder", "mock"]


BUILDER_TYPE_DICT = dict()
# TODO: napoleon variable docstring
BUILDER_TYPE_DICT[BuilderType.MOCK] = MockBuilder
BUILDER_TYPE_DICT[BuilderType.NONE] = Builder

